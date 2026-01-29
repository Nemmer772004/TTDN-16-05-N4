# -*- coding: utf-8 -*-
from odoo import models, fields, api
from odoo.exceptions import ValidationError, UserError
from datetime import datetime, timedelta

class DonNghiPhep(models.Model):
    _name = 'don_nghi_phep'
    _description = 'Quản lý nghỉ phép'
    _order = 'ngay_tao desc'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'ma_don'
    
    ma_don = fields.Char(string='Mã đơn', readonly=True, default='New', copy=False)
    
    # Thông tin nhân viên
    nhan_vien_id = fields.Many2one('nhan_vien', string='Nhân viên', required=True,
                                    default=lambda self: self._get_current_employee(),
                                    tracking=True)
    ma_dinh_danh = fields.Char(related='nhan_vien_id.ma_dinh_danh', string='Mã NV', store=True)
    don_vi_id = fields.Many2one('don_vi', string='Đơn vị',
                                related='nhan_vien_id.lich_su_cong_tac_ids.don_vi_id',
                                store=True)
    
    # Thời gian nghỉ
    ngay_bat_dau = fields.Date(string='Ngày bắt đầu', required=True, tracking=True)
    ngay_ket_thuc = fields.Date(string='Ngày kết thúc', required=True, tracking=True)
    so_ngay_nghi = fields.Float(string='Số ngày nghỉ', compute='_compute_so_ngay', store=True)
    
    # Thời gian trong ngày (nếu nghỉ nửa ngày)
    nghi_ca = fields.Selection([
        ('ca_ngay', 'Cả ngày'),
        ('sang', 'Buổi sáng'),
        ('chieu', 'Buổi chiều'),
    ], string='Nghỉ ca', default='ca_ngay', required=True)
    
    # Loại nghỉ phép
    loai_nghi_phep = fields.Selection([
        ('phep_nam', 'Phép năm'),
        ('phep_le', 'Nghỉ lễ'),
        ('om', 'Ốm đau'),
        ('ket_hon', 'Kết hôn'),
        ('ma_chay', 'Ma chay'),
        ('thai_san', 'Thai sản'),
        ('hoc_tap', 'Học tập, đào tạo'),
        ('che_do', 'Chế độ (hiếu, hỷ)'),
        ('khac', 'Khác'),
    ], string='Loại nghỉ phép', required=True, default='phep_nam', tracking=True)
    
    co_luong = fields.Boolean(string='Có lương', default=True,
                              help='Đánh dấu nếu loại nghỉ phép này được hưởng lương')
    
    # Lý do và file đính kèm
    ly_do = fields.Text(string='Lý do nghỉ', required=True)
    file_dinh_kem = fields.Binary(string='File đính kèm', 
                                   help='Giấy tờ chứng minh (đơn, giấy khám bệnh,...)')
    ten_file = fields.Char(string='Tên file')
    
    # Người thay thế
    nguoi_thay_the_id = fields.Many2one('nhan_vien', string='Người thay thế công việc')
    ghi_chu_cong_viec = fields.Text(string='Ghi chú bàn giao công việc')
    
    # Phê duyệt
    trang_thai = fields.Selection([
        ('nhap', 'Nháp'),
        ('cho_duyet', 'Chờ duyệt'),
        ('da_duyet', 'Đã duyệt'),
        ('tu_choi', 'Từ chối'),
        ('huy', 'Đã hủy'),
    ], string='Trạng thái', default='nhap', tracking=True, required=True)
    
    nguoi_duyet_id = fields.Many2one('res.users', string='Người phê duyệt', readonly=True)
    ngay_duyet = fields.Datetime(string='Ngày phê duyệt', readonly=True)
    ly_do_tu_choi = fields.Text(string='Lý do từ chối')
    
    # Thông tin tạo
    ngay_tao = fields.Datetime(string='Ngày tạo', default=fields.Datetime.now, readonly=True)
    nguoi_tao_id = fields.Many2one('res.users', string='Người tạo', 
                                    default=lambda self: self.env.user, readonly=True)
    
    # Số ngày phép còn lại
    so_ngay_phep_con_lai = fields.Float(string='Số ngày phép còn lại', 
                                         compute='_compute_ngay_phep_con_lai')
    
    @api.model
    def _get_current_employee(self):
        """Lấy nhân viên hiện tại dựa trên user đang đăng nhập"""
        # Logic để map user -> nhân viên (có thể cần customize)
        return self.env['nhan_vien'].search([('email', '=', self.env.user.email)], limit=1)
    
    @api.model
    def create(self, vals):
        if vals.get('ma_don', 'New') == 'New':
            vals['ma_don'] = self.env['ir.sequence'].next_by_code('don_nghi_phep') or 'New'
        return super(DonNghiPhep, self).create(vals)
    
    @api.depends('ngay_bat_dau', 'ngay_ket_thuc', 'nghi_ca')
    def _compute_so_ngay(self):
        for record in self:
            if record.ngay_bat_dau and record.ngay_ket_thuc:
                if record.ngay_ket_thuc < record.ngay_bat_dau:
                    raise ValidationError('Ngày kết thúc phải sau hoặc bằng ngày bắt đầu!')
                
                delta = record.ngay_ket_thuc - record.ngay_bat_dau
                so_ngay = delta.days + 1
                
                # Tính số ngày làm việc (trừ thứ 7, chủ nhật)
                so_ngay_lam_viec = 0
                current_date = record.ngay_bat_dau
                while current_date <= record.ngay_ket_thuc:
                    # weekday: 0=Monday, 6=Sunday
                    if current_date.weekday() < 5:  # Thứ 2-6
                        so_ngay_lam_viec += 1
                    current_date += timedelta(days=1)
                
                # Nếu nghỉ nửa ngày
                if record.nghi_ca != 'ca_ngay' and so_ngay_lam_viec == 1:
                    record.so_ngay_nghi = 0.5
                else:
                    record.so_ngay_nghi = so_ngay_lam_viec
            else:
                record.so_ngay_nghi = 0
    
    @api.depends('nhan_vien_id', 'so_ngay_nghi', 'loai_nghi_phep')
    def _compute_ngay_phep_con_lai(self):
        for record in self:
            if record.nhan_vien_id and record.loai_nghi_phep == 'phep_nam':
                # Tính tổng số ngày đã nghỉ trong năm
                year = fields.Date.today().year
                domain = [
                    ('nhan_vien_id', '=', record.nhan_vien_id.id),
                    ('trang_thai', '=', 'da_duyet'),
                    ('loai_nghi_phep', '=', 'phep_nam'),
                    ('ngay_bat_dau', '>=', f'{year}-01-01'),
                    ('ngay_bat_dau', '<=', f'{year}-12-31'),
                ]
                # Chỉ loại trừ record hiện tại nếu nó đã tồn tại trong database
                # _origin.id lấy ID thật, không bao gồm NewId
                if record._origin.id:
                    domain.append(('id', '!=', record._origin.id))
                
                approved_leaves = self.search(domain)
                tong_ngay_da_nghi = sum(approved_leaves.mapped('so_ngay_nghi'))
                
                # Giả sử mỗi nhân viên có 12 ngày phép năm
                so_ngay_phep_nam = 12.0
                record.so_ngay_phep_con_lai = so_ngay_phep_nam - tong_ngay_da_nghi - record.so_ngay_nghi
            else:
                record.so_ngay_phep_con_lai = 0.0
    
    @api.constrains('ngay_bat_dau', 'ngay_ket_thuc', 'nhan_vien_id', 'trang_thai')
    def _check_overlap(self):
        """Kiểm tra trùng lặp đơn nghỉ phép"""
        for record in self:
            if record.trang_thai in ['cho_duyet', 'da_duyet']:
                overlapping = self.search([
                    ('nhan_vien_id', '=', record.nhan_vien_id.id),
                    ('trang_thai', 'in', ['cho_duyet', 'da_duyet']),
                    ('id', '!=', record.id),
                    '|',
                    '&', 
                    ('ngay_bat_dau', '<=', record.ngay_bat_dau),
                    ('ngay_ket_thuc', '>=', record.ngay_bat_dau),
                    '&',
                    ('ngay_bat_dau', '<=', record.ngay_ket_thuc),
                    ('ngay_ket_thuc', '>=', record.ngay_ket_thuc),
                ])
                if overlapping:
                    raise ValidationError(f'Đã có đơn nghỉ phép trong khoảng thời gian này! Mã đơn: {overlapping[0].ma_don}')
    
    def action_gui_duyet(self):
        """Gửi đơn nghỉ phép đi phê duyệt"""
        self.ensure_one()
        if self.trang_thai != 'nhap':
            raise UserError('Chỉ có thể gửi duyệt đơn đang ở trạng thái Nháp!')
        
        # Kiểm tra số ngày phép còn lại
        if self.loai_nghi_phep == 'phep_nam' and self.so_ngay_phep_con_lai < 0:
            raise ValidationError(f'Không đủ số ngày phép! Còn lại: {self.so_ngay_phep_con_lai + self.so_ngay_nghi} ngày')
        
        self.trang_thai = 'cho_duyet'
        self.message_post(body=f"Đơn nghỉ phép đã được gửi phê duyệt")
        
        # TODO: Gửi email thông báo cho người phê duyệt
    
    def action_phe_duyet(self):
        """Phê duyệt đơn nghỉ phép"""
        self.ensure_one()
        if self.trang_thai != 'cho_duyet':
            raise UserError('Chỉ có thể phê duyệt đơn đang ở trạng thái Chờ duyệt!')
        
        self.write({
            'trang_thai': 'da_duyet',
            'nguoi_duyet_id': self.env.user.id,
            'ngay_duyet': fields.Datetime.now(),
        })
        self.message_post(body=f"Đơn nghỉ phép đã được phê duyệt bởi {self.env.user.name}")
        
        # TODO: Gửi email thông báo cho nhân viên
    
    def action_tu_choi(self):
        """Từ chối đơn nghỉ phép"""
        self.ensure_one()
        if self.trang_thai != 'cho_duyet':
            raise UserError('Chỉ có thể từ chối đơn đang ở trạng thái Chờ duyệt!')
        
        return {
            'name': 'Lý do từ chối',
            'type': 'ir.actions.act_window',
            'res_model': 'don_nghi_phep',
            'view_mode': 'form',
            'view_id': self.env.ref('quan_ly_nhan_su.view_don_nghi_phep_tu_choi_form').id,
            'res_id': self.id,
            'target': 'new',
        }
    
    def action_confirm_tu_choi(self):
        """Xác nhận từ chối"""
        self.ensure_one()
        if not self.ly_do_tu_choi:
            raise UserError('Vui lòng nhập lý do từ chối!')
        
        self.write({
            'trang_thai': 'tu_choi',
            'nguoi_duyet_id': self.env.user.id,
            'ngay_duyet': fields.Datetime.now(),
        })
        self.message_post(body=f"Đơn nghỉ phép đã bị từ chối. Lý do: {self.ly_do_tu_choi}")
    
    def action_huy(self):
        """Hủy đơn nghỉ phép"""
        self.ensure_one()
        if self.trang_thai not in ['nhap', 'cho_duyet']:
            raise UserError('Không thể hủy đơn đã được phê duyệt hoặc đã từ chối!')
        
        self.trang_thai = 'huy'
        self.message_post(body="Đơn nghỉ phép đã được hủy")
    
    def action_quay_lai_nhap(self):
        """Quay lại trạng thái nháp"""
        self.ensure_one()
        if self.trang_thai not in ['cho_duyet', 'tu_choi']:
            raise UserError('Chỉ có thể chuyển về nháp từ trạng thái Chờ duyệt hoặc Từ chối!')
        
        self.trang_thai = 'nhap'
        self.ly_do_tu_choi = False
        self.message_post(body="Đơn nghỉ phép đã được chuyển về trạng thái Nháp")
