# Báo cáo LaTeX

Mở thư mục gốc của dự án trong VS Code, sau đó mở `docs/data_warehouse/main.tex` cho môn Nhà kho dữ liệu và tích hợp hoặc `docs/BI/main.tex` cho môn BI.
Dùng lệnh **LaTeX Workshop: Build LaTeX project** (hoặc `Ctrl+Alt+B`)
và chọn recipe **latexmk (XeLaTeX)** nếu được hỏi. PDF được tạo tại
`docs/data_warehouse/build/main.pdf` hoặc `docs/BI/build/main.pdf`; dùng **LaTeX Workshop: View LaTeX PDF** để xem.

Mẫu dùng XeLaTeX để gõ tiếng Việt UTF-8 với Times New Roman. Sửa thông tin
trang bìa và thay các đoạn hướng dẫn trong từng chương bằng nội dung thực tế
của nhóm. Đặt hình trong `docs/figures/` và chèn bằng `\includegraphics`.

Nếu VS Code chưa nhận lệnh sau khi cài MiKTeX hoặc Strawberry Perl, khởi động
lại VS Code rồi kiểm tra `latexmk`, `xelatex` và `perl` trong terminal.

link tutorial: https://www.youtube.com/watch?v=4lyHIQl4VM8&t=589s
