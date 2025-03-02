from odoo import models, fields

class DatPhong(models.Model):
    _name = "dat_phong"
    _description = "Đăng ký mượn phòng"

    phong_id = fields.Many2one("quan_ly_phong_hop", string="Phòng mượn", required=True)
    ten_nguoi_dat = fields.Char(string="Tên người mượn", required=True)
    email_nguoi_dat = fields.Char(string="Email người mượn")
    so_dien_thoai_nguoi_dat = fields.Char(string="Số điện thoại người mượn")
    id_nhan_vien = fields.Char(string="Mã nhân viên")
    thoi_gian_muon_du_kien = fields.Datetime(string="Thời gian mượn dự kiến" )
    thoi_gian_muon_thuc_te = fields.Datetime(string="Thời gian mượn thực tế" )
    thoi_gian_tra_du_kien = fields.Datetime(string="Thời gian trả dự kiến")
    thoi_gian_tra_thuc_te = fields.Datetime(string="Thời gian trả thực tế" )
    trang_thai = fields.Selection([
        ("chờ duyệt", "chờ duyệt"),
        ("đã duyệt", "đã duyệt"),
        ("đã hủy", "đã hủy")
    ], string="Trạng thái", default="sắp bắt đầu")
    