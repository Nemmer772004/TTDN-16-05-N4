from odoo import models, fields, api


class DonVi(models.Model):
    _name = 'don_vi'
    _description = 'Bảng chứa thông tin đơn vị'
    _rec_name = 'ten_don_vi'

    ma_don_vi = fields.Char("Mã đơn vị", required=True)
    ten_don_vi = fields.Char("Tên đơn vị", required=True)
    
    # Quản lý đơn vị
    truong_don_vi_id = fields.Many2one('nhan_vien', string="Trưởng đơn vị")
    pho_don_vi_ids = fields.Many2many('nhan_vien', 'don_vi_pho_rel',
                                       'don_vi_id', 'nhan_vien_id',
                                       string="Phó đơn vị")
    
    # Thống kê
    so_nhan_vien = fields.Integer("Số nhân viên", compute="_compute_so_nhan_vien", store=True)
    so_cuoc_hop = fields.Integer("Số cuộc họp", compute="_compute_thong_ke", store=True)
    so_lan_muon_thiet_bi = fields.Integer("Số lần mượn thiết bị", compute="_compute_thong_ke", store=True)
    
    @api.depends('truong_don_vi_id', 'pho_don_vi_ids')
    def _compute_so_nhan_vien(self):
        """Đếm số nhân viên trong đơn vị"""
        for record in self:
            lich_su_cong_tac = self.env['lich_su_cong_tac'].search([
                ('don_vi_id', '=', record.id)
            ])
            record.so_nhan_vien = len(set(lich_su_cong_tac.mapped('nhan_vien_id')))
    
    @api.depends('truong_don_vi_id')
    def _compute_thong_ke(self):
        """Tính toán thống kê về hoạt động của đơn vị"""
        for record in self:
            # TODO: Implement when integrating with meeting and equipment modules
            record.so_cuoc_hop = 0
            record.so_lan_muon_thiet_bi = 0