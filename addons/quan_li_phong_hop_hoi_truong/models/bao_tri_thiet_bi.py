from odoo import models, fields, api

class BaoTriThietBi(models.Model):
    _name = "bao_tri_thiet_bi"
    _description = "Lịch sử bảo trì thiết bị"
    _order = "ngay_bao_tri desc"

    thiet_bi_id = fields.Many2one("thiet_bi", string="Thiết bị", required=True, ondelete="cascade")
    phong_id = fields.Many2one("quan_ly_phong_hop", string="Phòng", related="thiet_bi_id.phong_id", store=True)
    
    ngay_bao_tri = fields.Date(string="Ngày bảo trì", required=True, default=fields.Date.today)
    nguoi_bao_tri = fields.Many2one("nhan_vien", string="Người bảo trì")
    
    loai_bao_tri = fields.Selection([
        ('dinh_ky', 'Bảo trì định kỳ'),
        ('sua_chua', 'Sửa chữa'),
        ('thay_the', 'Thay thế linh kiện'),
    ], string="Loại bảo trì", required=True, default="dinh_ky")
    
    van_de = fields.Text(string="Vấn đề", help="Mô tả vấn đề cần bảo trì")
    giai_phap = fields.Text(string="Giải pháp", help="Cách khắc phục")
    chi_phi = fields.Float(string="Chi phí (VNĐ)")
    
    trang_thai_truoc = fields.Selection([
        ('dang_su_dung', 'Đang sử dụng'),
        ('san_sang', 'Sẵn sàng'),
        ('can_bao_tri', 'Cần bảo trì'),
        ('hong', 'Hỏng'),
    ], string="Trạng thái trước bảo trì")
    
    trang_thai_sau = fields.Selection([
        ('dang_su_dung', 'Đang sử dụng'),
        ('san_sang', 'Sẵn sàng'),
        ('can_bao_tri', 'Cần bảo trì'),
        ('hong', 'Hỏng'),
    ], string="Trạng thái sau bảo trì", default="san_sang")
    
    ghi_chu = fields.Text(string="Ghi chú")
    
    @api.model
    def create(self, vals):
        """Lưu trạng thái trước khi bảo trì"""
        if vals.get('thiet_bi_id'):
            thiet_bi = self.env['thiet_bi'].browse(vals['thiet_bi_id'])
            vals['trang_thai_truoc'] = thiet_bi.trang_thai
        return super(BaoTriThietBi, self).create(vals)
