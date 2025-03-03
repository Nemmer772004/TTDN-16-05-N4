from odoo import models, fields, api

class QuanLyPhongHop(models.Model):
    _name = "quan_ly_phong_hop"
    _description = "Quản lý phòng họp, hội trường"

    name = fields.Char(string="Tên phòng họp", required=True)
    loai_phong = fields.Selection([
        ("Phòng_họp", "Phòng họp"),
        ("Hội_trường", "Hội trường"),
    ], string="Loại phòng", required=True, default="Phòng_họp")
    suc_chua = fields.Integer(string="Sức chứa")

    trang_thai = fields.Selection([
        ("Có_sẵn", "Có sẵn"),
        ("Đã_mượn", "Đã mượn"),
    ], string="Trạng thái", compute="_compute_trang_thai", store=True)

    dat_phong_ids = fields.One2many("dat_phong", "phong_id", string="Lịch sử mượn phòng")

    @api.depends("dat_phong_ids.trang_thai")
    def _compute_trang_thai(self):
        for record in self:
            active_bookings = record.dat_phong_ids.filtered(lambda r: r.trang_thai in ["chờ_duyệt", "đã_duyệt"])
            record.trang_thai = "Đã_mượn" if active_bookings else "Có_sẵn"
