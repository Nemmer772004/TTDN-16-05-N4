from odoo import models, fields, api
from datetime import datetime

class LichSuThayDoi(models.Model):
    _name = "lich_su_thay_doi"
    _description = "Lịch sử thay đổi trạng thái của phòng họp, hội trường"

    dat_phong_id = fields.Many2one("dat_phong", string="Mã đăng ký", required=True, ondelete="cascade")
    phong_id = fields.Many2one("quan_ly_phong_hop", string="Phòng", related="dat_phong_id.phong_id", store=True)
    nguoi_muon_id = fields.Many2one("nhan_vien", string="Người mượn", related="dat_phong_id.nguoi_muon_id", store=True)
    thoi_gian_muon_du_kien = fields.Datetime(string="Thời gian mượn dự kiến")
    thoi_gian_muon_thuc_te = fields.Datetime(string="Thời gian mượn thực tế")
    thoi_gian_tra_du_kien = fields.Datetime(string="Thời gian trả dự kiến")
    thoi_gian_tra_thuc_te = fields.Datetime(string="Thời gian trả thực tế")
    trang_thai = fields.Selection([
        ("chờ_duyệt", "Chờ duyệt"),
        ("đã_duyệt", "Đã duyệt"),
        ("đang_sử_dụng", "Đang sử dụng"),
        ("đã_hủy", "Đã hủy"),
        ("đã_trả", "Đã trả")
    ], string="Trạng thái")
    ngay_thay_doi = fields.Datetime(string="Ngày thay đổi", default=lambda self: datetime.now())
    
