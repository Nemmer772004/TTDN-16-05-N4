from odoo import models, fields, api
from datetime import datetime

class LichSuMuonTra(models.Model):
    _name = "lich_su_muon_tra"
    _description = "Lịch sử mượn trả phòng"

    dat_phong_id = fields.Many2one("dat_phong", string="Mã đăng ký", required=True, ondelete="cascade")
    phong_id = fields.Many2one("quan_ly_phong_hop", string="Phòng", related="dat_phong_id.phong_id", store=True)
    ten_nguoi_dat = fields.Char(string="Tên người mượn", related="dat_phong_id.ten_nguoi_dat", store=True)
    thoi_gian_muon_du_kien = fields.Datetime(string="Thời gian mượn dự kiến")
    thoi_gian_muon_thuc_te = fields.Datetime(string="Thời gian mượn thực tế")
    thoi_gian_tra_du_kien = fields.Datetime(string="Thời gian trả dự kiến")
    thoi_gian_tra_thuc_te = fields.Datetime(string="Thời gian trả thực tế")
    trang_thai = fields.Selection([
        ("chờ_duyệt", "Chờ duyệt"),
        ("đã_duyệt", "Đã duyệt"),
        ("đã_hủy", "Đã hủy"),
        ("đã_trả", "Đã trả")
    ], string="Trạng thái")
    ngay_thay_doi = fields.Datetime(string="Ngày thay đổi", default=lambda self: datetime.now())

