"""Application orchestration: plan, guard, compile, execute, and summarize."""

from __future__ import annotations

import logging
from uuid import uuid4

from dataagent.auth import EntraTokenProvider
from dataagent.catalog import SemanticCatalog
from dataagent.config import Settings, get_settings
from dataagent.dax_compiler import DaxCompiler
from dataagent.errors import ConfigurationError, DataAgentError, QueryValidationError
from dataagent.fabric_client import PowerBIRestClient
from dataagent.gemini_client import GeminiClient
from dataagent.query_guard import QueryGuard
from dataagent.result_normalizer import ResultNormalizer
from dataagent.schemas import Action, AgentResponse, QueryPlan

logger = logging.getLogger(__name__)


class DataAgentService:
    def __init__(
        self,
        settings: Settings | None = None,
        catalog: SemanticCatalog | None = None,
        fabric_client: PowerBIRestClient | None = None,
        gemini_client: GeminiClient | None = None,
    ) -> None:
        self.settings = settings or get_settings()
        self.catalog = catalog or SemanticCatalog(self.settings.semantic_catalog_path)
        self.catalog.validate_identity(
            self.settings.powerbi_workspace_id,
            self.settings.powerbi_semantic_model_id,
        )
        self.guard = QueryGuard(self.catalog, self.settings.max_result_rows)
        self.compiler = DaxCompiler(self.catalog)
        self.normalizer = ResultNormalizer(self.catalog, self.settings.max_result_rows)

        if fabric_client is None:
            token_provider = EntraTokenProvider(self.settings)
            fabric_client = PowerBIRestClient(self.settings, token_provider)
        self.fabric = fabric_client
        self.gemini = gemini_client or GeminiClient(self.settings, self.catalog)

    def health_check(self) -> dict[str, object]:
        model = self.fabric.health_check()
        expected_name = str(self.catalog.model.get("name", "")).strip().casefold()
        actual_name = str(model.get("name", "")).strip().casefold()
        if expected_name and actual_name != expected_name:
            raise ConfigurationError(
                "Visible semantic model name does not match the curated catalog"
            )
        return {
            **model,
            "catalog_version": self.catalog.version,
            "planner_model": self.settings.gemini_model_planner,
            "summarizer_model": self.settings.gemini_model_summarizer,
        }

    def answer(self, question: str, history: list[dict[str, str]] | None = None) -> AgentResponse:
        request_id = str(uuid4())
        plan: QueryPlan | None = None
        dax: str | None = None
        try:
            plan = self.gemini.plan(question, history)
            if plan.action == Action.CLARIFY:
                return AgentResponse(
                    request_id=request_id,
                    status="clarify",
                    title=plan.title,
                    text=plan.clarification_question or "Bạn có thể làm rõ câu hỏi không?",
                    query_plan=plan,
                )
            if plan.action == Action.REJECT:
                return AgentResponse(
                    request_id=request_id,
                    status="rejected",
                    title=plan.title,
                    text=plan.rejection_reason or "Yêu cầu này nằm ngoài phạm vi dữ liệu cho phép.",
                    query_plan=plan,
                )

            plan = self.guard.validate(plan)
            dax = self.compiler.compile(plan)
            raw_rows, api_warnings = self.fabric.execute_dax(dax)
            result = self.normalizer.normalize(raw_rows, api_warnings)
            warnings = [*result.warnings, *self._business_warnings(plan)]

            if not result.rows:
                return AgentResponse(
                    request_id=request_id,
                    status="empty",
                    title=plan.title,
                    text="Không tìm thấy dữ liệu phù hợp với các điều kiện truy vấn.",
                    warnings=warnings,
                    dax=dax,
                    query_plan=plan,
                )

            text = self.gemini.summarize(question, plan, result.rows, warnings)
            logger.info(
                "data_agent_request status=ok request_id=%s rows=%d catalog=%s",
                request_id,
                len(result.rows),
                self.catalog.version,
            )
            return AgentResponse(
                request_id=request_id,
                status="ok",
                title=plan.title,
                text=text,
                rows=result.rows,
                columns=result.columns,
                warnings=warnings,
                dax=dax,
                query_plan=plan,
            )
        except QueryValidationError as exc:
            return self._error_response(
                request_id,
                f"Kế hoạch truy vấn bị chặn bởi guardrail: {exc}",
                plan,
                dax,
            )
        except DataAgentError as exc:
            logger.warning(
                "data_agent_request status=error request_id=%s type=%s",
                request_id,
                type(exc).__name__,
            )
            return self._error_response(request_id, str(exc), plan, dax)
        except Exception:
            logger.exception("Unexpected data-agent failure request_id=%s", request_id)
            return self._error_response(
                request_id,
                "Đã xảy ra lỗi không mong đợi. Hãy dùng request ID để kiểm tra log.",
                plan,
                dax,
            )

    @staticmethod
    def _error_response(
        request_id: str,
        message: str,
        plan: QueryPlan | None,
        dax: str | None,
    ) -> AgentResponse:
        return AgentResponse(
            request_id=request_id,
            status="error",
            title=plan.title if plan else "Không thể xử lý câu hỏi",
            text=message,
            query_plan=plan,
            dax=dax,
        )

    @staticmethod
    def _business_warnings(plan: QueryPlan) -> list[str]:
        warnings: list[str] = []
        if any(name in plan.measures for name in {"Stock Quantity", "Reorder Products"}):
            warnings.append(
                "Tồn kho là snapshot tại thời điểm quan sát, không phải lịch sử tồn kho."
            )
        if "Historical Demo Forecast Qty" in plan.measures:
            warnings.append(
                "Forecast này là mô phỏng lịch sử, không phải dự báo vận hành hiện tại."
            )
        if "Estimated Standard Margin" in plan.measures:
            warnings.append("Biên lợi nhuận là ước tính và phải đọc cùng Cost Coverage.")
        return warnings
