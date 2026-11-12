"""Convert the existing chapter drafts into editable LaTeX, without adding findings."""
from pathlib import Path
import re
import zipfile
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1] / 'docs' / 'data_warehouse'
SOURCE = ROOT / 'source' / 'content'
NS = {'w': 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'}


def escape(text):
    for a, b in [('\\', r'\textbackslash{}'), ('&', r'\&'), ('%', r'\%'), ('_', r'\_'), ('#', r'\#')]:
        text = text.replace(a, b)
    return text


def references(text):
    text = text.replace('Chaudhuri và Dayal (1997)', r'Chaudhuri và Dayal~\citeyearpar{chaudhuri1997}')
    text = text.replace('Microsoft (2024)', r'Microsoft~\citeyearpar{microsoft-scenario}')
    text = text.replace('(Microsoft, 2024)', r'\citep{microsoft-scenario}')
    return text


def template_headings(lines):
    """Keep the original extarticle heading levels and page style."""
    return [line.replace(r'\subsection{', r'\subsubsection{')
                .replace(r'\section{', r'\subsection{')
                .replace(r'\chapter{', r'\chuong{') for line in lines]


def write_ch1():
    src = (SOURCE / 'semidone_c1.md').read_text(encoding='utf-8')
    src = src.split('Chaudhuri, S., & Dayal, U. (1997).')[0]
    lines = [r'\chapter{GIỚI THIỆU TỔNG QUAN}', '']
    for block in re.split(r'\n\s*\n', src):
        block = block.strip()
        if not block:
            continue
        head = re.sub(r'^[#* ]+|[* ]+$', '', block)
        m = re.match(r'^(1\.(?:\d+)(?:\.\d+)?)\.?\s+(.+)$', head)
        if m and len(block.splitlines()) == 1:
            if m.group(1) == '1.4.1':
                lines.extend([r'\subsection{Đối tượng nghiên cứu}', ''])
                continue
            if m.group(1) == '1.4.2':
                lines.extend([
                    r'\subsection{Phạm vi nghiệp vụ bán hàng}',
                    r'Dự án tập trung vào đơn hàng, chi tiết đơn hàng, sản phẩm, khách hàng và khu vực bán hàng. Các chỉ tiêu được xem xét gồm doanh thu, số lượng bán và số đơn hàng theo thời gian, sản phẩm, khách hàng và khu vực.',
                    ''
                ])
                continue
            level = 'section' if m.group(1).count('.') == 1 else 'subsection'
            lines.extend([f'\\{level}{{{escape(m.group(2))}}}', ''])
            continue
        if block.startswith('Về phạm vi dữ liệu,'):
            lines.extend([r'\subsection{Phạm vi dữ liệu}', ''])
        elif block.startswith('Về phạm vi xây dựng hệ thống,'):
            lines.extend([r'\subsection{Phạm vi triển khai}', ''])
        # Markdown bold is only used for headings in this draft.
        text = escape(block.replace('**', '').replace('\n', ' '))
        text = references(text)
        text = text.replace('trong cùng môi trường.', r'trong cùng môi trường~\citep{microsoft-fabric}.')
        text = text.replace('Microsoft lựa chọn bổ sung Analysis Services để cải thiện truy vấn và tái sử dụng cách tính.', r'Microsoft lựa chọn bổ sung Analysis Services để cải thiện truy vấn và tái sử dụng cách tính~\citep{microsoft-scenario}.')
        text = text.replace('Microsoft nêu mô hình hình sao và hình tuyết', r'Microsoft~\citeyearpar{microsoft-warehouse} nêu mô hình hình sao và hình tuyết')
        lines.extend([text, ''])
    lines.extend([
        r'\section{Công nghệ và nền tảng sử dụng}',
        r'\subsection{Microsoft Fabric}',
        r'Microsoft Fabric cung cấp các thành phần tích hợp, lưu trữ, xử lý và trình bày dữ liệu trong cùng một môi trường~\citep{microsoft-fabric}. Đồ án sử dụng nền tảng này để tổ chức luồng từ dữ liệu giao dịch đến dữ liệu phục vụ phân tích.',
        r'\subsection{OneLake và Lakehouse}',
        r'OneLake là lớp lưu trữ dùng chung trong Fabric; Lakehouse là nơi nhóm dự kiến tổ chức dữ liệu qua các tầng xử lý trước khi nạp vào kho dữ liệu~\citep{microsoft-fabric}.',
        r'\subsection{Fabric Data Factory}',
        r'Fabric Data Factory được định hướng dùng để thu thập và điều phối các bước nạp, chuyển đổi dữ liệu. Cấu hình pipeline và lịch chạy sẽ được trình bày ở chương triển khai sau khi hoàn tất thử nghiệm~\citep{microsoft-fabric}.',
        r'\subsection{Fabric Data Warehouse}',
        r'Fabric Data Warehouse là lớp dữ liệu quan hệ phục vụ truy vấn phân tích. Mô hình dự kiến dùng bảng sự kiện bán hàng và các chiều thời gian, sản phẩm, khách hàng, khu vực~\citep{microsoft-warehouse}.',
        r'\subsection{Fabric Data Science}',
        r'Nhóm dự kiến dùng notebook trong Fabric để thử nghiệm dự báo từ dữ liệu lịch sử. Biến đầu vào, cách tách tập huấn luyện và kết quả đánh giá chỉ được xác định sau khi kiểm tra dữ liệu thực tế~\citep{microsoft-fabric}.',
        r'\subsection{Power BI và Web Application}',
        r'Power BI là lớp trình bày các chỉ tiêu bán hàng từ mô hình phân tích. Web Application nằm trong đề cương dự án; phạm vi và cách kết nối cần được xác nhận khi triển khai~\citep{microsoft-fabric}.',
        ''
    ])
    (ROOT / 'chapter-1.tex').write_text('\n'.join(template_headings(lines)), encoding='utf-8')


def write_ch2():
    with zipfile.ZipFile(SOURCE / 'docs (2).docx') as z:
        doc = ET.fromstring(z.read('word/document.xml'))
        paragraphs = [''.join(t.text or '' for t in p.findall('.//w:t', NS)).strip()
                      for p in doc.findall('.//w:p', NS)]
        image_dir = ROOT / 'images' / 'chapter-2'
        image_dir.mkdir(parents=True, exist_ok=True)
        (image_dir / 'adventureworks-oltp-schema.png').write_bytes(z.read('word/media/image1.png'))
    lines = [r'\chapter{MÔ TẢ VÀ PHÂN TÍCH DỮ LIỆU BÁN HÀNG}', '']
    for p in paragraphs:
        if not p:
            continue
        if p.startswith('2.1. Tổng quan'):
            lines.extend([r'\section{Tổng quan về Adventure Works Cycles}', ''])
        elif p.startswith('2.1.1. Nguồn dữ liệu'):
            lines.extend([
                r'\section{Tổng quan hoạt động bán hàng}',
                r'\subsection{Quy trình bán hàng}',
                r'Trong dữ liệu nguồn, một đơn hàng gồm bản ghi đầu đơn tại \texttt{Sales.SalesOrderHeader} và các dòng hàng tại \texttt{Sales.SalesOrderDetail}. Đầu đơn lưu ngày đặt hàng, khách hàng, khu vực, kênh đặt hàng và trạng thái; dòng hàng lưu sản phẩm, số lượng, đơn giá và chiết khấu. Quan hệ này cho phép đi từ giao dịch phát sinh đến số đo doanh thu ở mức từng sản phẩm trong đơn~\citep{aw-samples}.',
                r'\subsection{Các đối tượng tham gia hoạt động bán hàng}',
                r'Các đối tượng chính trong phạm vi phân tích là đơn hàng, sản phẩm, khách hàng và lãnh thổ bán hàng. Dữ liệu sản phẩm nối tiếp tới phân nhóm và danh mục; khách hàng có thể gắn với cá nhân hoặc cửa hàng. Những quan hệ này được mô tả trong script nguồn \texttt{AdventureWorks/raw/instawdb.sql} và sơ đồ ở Hình~\ref{fig:aw-oltp-schema}.',
                r'\subsection{Các chỉ tiêu đánh giá hoạt động bán hàng}',
                r'Các chỉ tiêu dự kiến gồm doanh thu dòng hàng, số lượng sản phẩm bán và số đơn hàng. \texttt{LineTotal} của dòng hàng được định nghĩa từ đơn giá, tỷ lệ chiết khấu và số lượng; \texttt{TotalDue} ở đầu đơn gồm tạm tính, thuế và phí vận chuyển. Khi so sánh hai mức số đo phải nêu rõ có cộng thuế và phí vận chuyển hay không~\citep{aw-samples}.',
                r'\section{Nguồn gốc và cấu trúc dữ liệu}',
                r'\subsection{Nguồn dữ liệu Adventure Works}', ''
            ])
        elif p.startswith('2.1.2. Cấu trúc dữ liệu'):
            lines.extend([r'\subsection{Cấu trúc dữ liệu nguồn}', ''])
        elif p.startswith('Bảng xx:'):
            lines.extend([
                r'\begin{table}[htbp]\centering',
                r'\caption{Các lược đồ nghiệp vụ trong AdventureWorks OLTP}',
                r'\label{tab:aw-schemas}',
                r'\begin{tabularx}{\textwidth}{|l|X|}\hline',
                r'\textbf{Lược đồ} & \textbf{Vai trò} \\ \hline',
                r'HumanResources & Thông tin nhân sự \\ \hline',
                r'Person & Thông tin cá nhân, liên hệ và địa chỉ \\ \hline',
                r'Production & Sản phẩm và hoạt động sản xuất \\ \hline',
                r'Purchasing & Mua hàng và nhà cung cấp \\ \hline',
                r'Sales & Bán hàng và khách hàng \\ \hline',
                r'\end{tabularx}', r'\end{table}', ''
            ])
        elif p in ('Lược đồ', 'Mô tả', 'Human Resources', 'Person', 'Production', 'Purchasing', 'Sales',
                   'Lưu thông tin nhân sự của công ty', 'Lưu thông tin cá nhân, liên hệ và địa chỉ',
                   'Quản lý sản phẩm và hoạt động sản xuất', 'Quản lý việc mua hàng và nhà cung cấp',
                   'Ghi nhận hoạt động bán hàng và khách hàng'):
            continue
        elif p.startswith('Hình xx:'):
            lines.extend([
                r'\begin{figure}[H]\centering',
                r'\includegraphics[width=\textwidth,height=0.6\textheight,keepaspectratio]{chapter-2/adventureworks-oltp-schema.png}',
                r'\caption{Sơ đồ tổng quát AdventureWorks OLTP 2008 (nguồn: \citealp{aw-schema}).}',
                r'\label{fig:aw-oltp-schema}', r'\end{figure}', ''
            ])
        else:
            text = references(escape(p))
            if p.startswith('Bộ AdventureWorks do Microsoft công bố'):
                text = text.rstrip('.') + r'~\citep{aw-samples}.'
            if p.startswith('Adventure Works Cycles phù hợp'):
                text = text.rstrip('.') + r'~\citep{microsoft-scenario}.'
            lines.extend([text, ''])
    lines.extend([
        r'\subsection{Các bảng dữ liệu phục vụ hoạt động bán hàng}',
        r'Nhóm bảng lõi gồm \texttt{SalesOrderHeader}, \texttt{SalesOrderDetail}, \texttt{Customer}, \texttt{SalesTerritory}, \texttt{Product}, \texttt{ProductSubcategory} và \texttt{ProductCategory}. Các bảng \texttt{Person} và \texttt{Store} bổ sung thông tin mô tả khách hàng. Khi triển khai cần kiểm tra khả năng nối từng bảng và cách xử lý khóa ngoại thiếu giá trị trước khi dùng làm chiều phân tích. Cấu trúc cột được đối chiếu từ \texttt{AdventureWorks/raw/instawdb.sql}~\citep{aw-samples}.',
        r'\subsection{Mối quan hệ giữa các bảng dữ liệu}',
        r'\texttt{SalesOrderDetail.SalesOrderID} nối với \texttt{SalesOrderHeader.SalesOrderID}; \texttt{ProductID} nối dòng hàng với sản phẩm. \texttt{CustomerID} và \texttt{TerritoryID} ở đầu đơn dẫn đến khách hàng và lãnh thổ. Từ sản phẩm có thể đi qua \texttt{ProductSubcategoryID} rồi \texttt{ProductCategoryID} để phân tích theo nhóm. Đây là đường nối dự kiến cho mô hình phân tích; số bản ghi mất liên kết cần được kiểm tra trên dữ liệu đã nạp.',
        r'\section{Khám phá và trực quan hóa dữ liệu}',
        r'\subsection{Phân tích doanh thu theo kênh bán hàng}',
        r'Cột \texttt{OnlineOrderFlag} ở đầu đơn có thể dùng để tách đơn đặt trực tuyến và đơn qua kênh khác. Bảng tổng hợp cần dùng cùng quy tắc trạng thái đơn và cùng định nghĩa doanh thu cho cả hai kênh.',
        r'\subsection{Phân tích doanh thu theo nhóm sản phẩm}',
        r'\texttt{ProductSubcategory} và \texttt{ProductCategory} cung cấp hai cấp phân nhóm. Khi tổng hợp, cần giữ cả sản phẩm chưa có phân nhóm để không làm mất doanh thu.',
        r'\subsection{Phân tích doanh thu theo thời gian}',
        r'\texttt{OrderDate} là mốc đặt hàng; \texttt{ShipDate} là mốc giao hàng và có thể trống. Nhóm sẽ chọn một ngày nghiệp vụ thống nhất trước khi tính chuỗi doanh thu theo tháng và năm.',
        r'\subsection{Phân tích khách hàng}',
        r'\texttt{CustomerID} cho phép đếm khách hàng phát sinh đơn. Việc phân loại cá nhân và cửa hàng dựa vào \texttt{PersonID} và \texttt{StoreID}; các trường hợp hai khóa cùng có giá trị cần được đối chiếu với định nghĩa trong dữ liệu nguồn.',
        r'\subsection{Phân tích doanh thu theo khu vực}',
        r'\texttt{TerritoryID} trên đầu đơn nối với \texttt{SalesTerritory}, nơi có tên lãnh thổ, quốc gia và nhóm khu vực. Doanh thu theo khu vực sẽ dùng lãnh thổ ghi tại thời điểm đơn hàng, tránh suy ngược từ địa chỉ hiện tại của khách hàng.',
        r'\section{Xác định yêu cầu dữ liệu cho giải pháp}',
        r'\subsection{Xác định quy trình nghiệp vụ}',
        r'Quy trình được chọn là bán hàng. Dữ liệu đầu đơn và dòng hàng là cơ sở để theo dõi doanh thu, số lượng bán và số đơn hàng theo các chiều phân tích.',
        r'\subsection{Xác định mức độ chi tiết dữ liệu}',
        r'Bảng sự kiện bán hàng dự kiến có một dòng cho mỗi \texttt{SalesOrderDetailID}. Mức chi tiết này giữ được liên hệ với sản phẩm, số lượng, giá và chiết khấu của từng dòng; các thuộc tính đầu đơn được đưa vào qua \texttt{SalesOrderID}.',
        r'\subsection{Xác định các chiều phân tích}',
        r'Những chiều tối thiểu gồm ngày đặt hàng, sản phẩm, khách hàng, lãnh thổ và kênh bán.',
        r'\subsection{Xác định các chỉ tiêu đo lường}',
        r'Các số đo tối thiểu gồm số lượng, doanh thu dòng hàng và số đơn hàng phân biệt. Thuế và phí vận chuyển ở mức đầu đơn sẽ được trình bày riêng để tránh cộng lặp khi một đơn có nhiều dòng.',
        r'\subsection{Xác định yêu cầu dữ liệu cho Machine Learning}',
        r'Bài toán dự báo doanh số cần chuỗi thời gian được tổng hợp ở một mức hạt và đơn vị tiền thống nhất. Tập huấn luyện và kiểm tra sẽ được tách theo thời gian; kết quả dự báo phải ghi rõ kỳ dự báo, dữ liệu lịch sử và sai số đánh giá trước khi đưa vào báo cáo.',
        ''
    ])
    (ROOT / 'chapter-2.tex').write_text('\n'.join(template_headings(lines)), encoding='utf-8')


if __name__ == '__main__':
    write_ch1()
    write_ch2()

