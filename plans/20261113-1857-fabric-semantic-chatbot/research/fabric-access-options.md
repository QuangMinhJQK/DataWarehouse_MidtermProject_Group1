# Nghiên cứu đường truy cập Fabric Semantic Model

Ngày kiểm tra: 13/11/2026. Nguồn ưu tiên: Microsoft Learn.

## So sánh

| Phương án | Điểm mạnh | Điểm yếu | Quyết định |
| --- | --- | --- | --- |
| Execute Queries REST + service principal | Unattended, Python nhẹ, credential-only | Không hỗ trợ model có RLS/SSO; REST không introspect schema | **MVP** |
| Execute Queries REST + delegated user | Giữ identity/RLS | OAuth/token cache từng user; cần Read + Build | Phase sau nếu cần |
| Fabric IQ MCP | GA; schema/value search/query; giữ RLS/OLS; không cần Premium/Build | Chỉ delegated OAuth; MCP orchestration phức tạp | Provider tương lai |
| XMLA | Metadata/DMV, DAX/MDX | Cần PPU/Premium/Fabric capacity; Python/.NET nặng | Không dùng MVP |
| Truy vấn Warehouse SQL | Dễ query raw data | Bỏ qua measure/filter context của Semantic Model | Không chọn |

## Execute Queries REST contract

```http
POST https://api.powerbi.com/v1.0/myorg/datasets/{semanticModelId}/executeQueries
Authorization: Bearer <token>
Content-Type: application/json

{"queries":[{"query":"EVALUATE ..."}],"serializerSettings":{"includeNulls":true}}
```

- Tenant phải bật `Dataset Execute Queries REST API`.
- Caller cần Read + Build. Delegated scope: `Dataset.Read.All` hoặc `Dataset.ReadWrite.All`.
- SP cần tenant setting cho service principals và quyền workspace/model phù hợp.
- SP không hỗ trợ model có RLS hoặc SSO; `impersonatedUserName` không khắc phục giới hạn này.
- Chỉ DAX; không MDX, INFO functions hoặc DMV.
- Mỗi call: một query, một result table.
- Server caps: 100,000 rows hoặc 1,000,000 values; 15 MB; 120 requests/phút/user.
- HTTP 200 vẫn có thể chứa error/truncation; client phải kiểm tra body.

App đặt caps thấp hơn: 200 rows/UI, tối đa 100 aggregate rows gửi Gemini, 2 group dimensions, timeout 30s và không auto-retry lỗi 400.

## Auth MVP

```env
FABRIC_AUTH_MODE=service_principal
AZURE_TENANT_ID=
AZURE_CLIENT_ID=
AZURE_CLIENT_SECRET=
POWERBI_WORKSPACE_ID=d0eaee60-9f3e-47b2-8aee-bbd327ab2062
POWERBI_SEMANTIC_MODEL_ID=
POWERBI_SCOPE=https://analysis.windows.net/powerbi/api/.default
```

- MSAL confidential client lấy token; không in/cache token ra disk mặc định.
- Client secret chỉ dành local/demo, lưu env/Streamlit Secrets và gitignore.
- Production ưu tiên certificate/secret manager hoặc delegated identity.
- Nếu model có RLS: dùng delegated user; user cuối không được là Member/Contributor nếu cần RLS được áp dụng.

## License gate

External chatbot tránh điều kiện paid F2/P1 của native Fabric Data Agent, nhưng không tạo thêm quyền truy cập Semantic Model. License/workspace/capacity hiện hữu vẫn áp dụng. Vì vậy phase 1 phải fail-fast bằng known-good Execute Queries request; nếu gate này thất bại thì chưa được code tiếp như thể data access đã tồn tại.

## Nguồn

- [Execute Queries REST API](https://learn.microsoft.com/en-us/rest/api/power-bi/datasets/execute-queries)
- [Semantic model permissions](https://learn.microsoft.com/en-us/power-bi/connect-data/service-datasets-permissions)
- [Service principal setup](https://learn.microsoft.com/en-us/power-bi/developer/embedded/embed-service-principal)
- [Fabric IQ MCP](https://learn.microsoft.com/en-us/fabric/iq/connectors/fabric-iq-mcp)
- [XMLA endpoint connectivity](https://learn.microsoft.com/en-us/fabric/enterprise/powerbi/service-premium-connect-tools)
- [Native Fabric Data Agent prerequisites](https://learn.microsoft.com/en-us/fabric/data-science/concept-data-agent)

