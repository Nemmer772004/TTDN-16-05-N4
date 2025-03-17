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
        ("Trống", "Trống"),
        ("Đã_mượn", "Đã mượn"),
        ("Đang_sử_dụng", "Đang sử dụng"),
    ], string="Trạng thái", compute="_compute_trang_thai", store=True)

    dat_phong_ids = fields.One2many("dat_phong", "phong_id", string="Lịch sử mượn phòng")
    lich_dat_phong_ids = fields.One2many("dat_phong", "phong_id", string="Lịch đặt phòng", domain=[("trang_thai", "!=", "đã_trả")])

    @api.depends("dat_phong_ids.trang_thai")
    def _compute_trang_thai(self):
        for record in self:
            active_bookings = record.dat_phong_ids.filtered(lambda r: r.trang_thai in ["đã_duyệt", "đang_sử_dụng"])
            using_bookings = record.dat_phong_ids.filtered(lambda r: r.trang_thai == "đang_sử_dụng")
            canceled_or_returned = record.dat_phong_ids.filtered(lambda r: r.trang_thai in ["đã_hủy", "đã_trả"])

            if using_bookings:
                record.trang_thai = "Đang_sử_dụng"
            elif active_bookings:
                record.trang_thai = "Đã_mượn"
            elif canceled_or_returned:
                record.trang_thai = "Trống"
            else:
                record.trang_thai = "Trống"
