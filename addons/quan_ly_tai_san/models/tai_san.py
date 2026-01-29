# -*- coding: utf-8 -*-
from odoo import models, fields, api
from datetime import datetime, date
from dateutil.relativedelta import relativedelta


class TaiSan(models.Model):
    _name = 'tai_san'
    _description = 'Quản lý Tài sản'
    _order = 'ma_tai_san desc'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    # Thông tin cơ bản
    ma_tai_san = fields.Char(
        string='Mã tài sản',
        required=True,
        copy=False,
        readonly=True,
        default=lambda self: 'New'
    )
    name = fields.Char(string='Tên tài sản', required=True, tracking=True)
    
    loai_tai_san = fields.Selection([
        ('thiet_bi_dien_tu', 'Thiết bị điện tử'),
        ('noi_that', 'Nội thất'),
        ('phuong_tien', 'Phương tiện'),
        ('thiet_bi_van_phong', 'Thiết bị văn phòng'),
        ('may_moc', 'Máy móc'),
        ('khac', 'Khác'),
    ], string='Loại tài sản', required=True, tracking=True)
    
    # Thông tin tài chính
    gia_tri = fields.Float(string='Giá trị (VNĐ)', required=True, tracking=True)
    gia_tri_thanh_ly = fields.Float(
        string='Giá trị thanh lý dự kiến (VNĐ)',
        default=0,
        help='Giá trị còn lại khi thanh lý (scrap value)'
    )
    ngay_mua = fields.Date(string='Ngày mua', required=True, default=fields.Date.today, tracking=True)
    ngay_bat_dau_su_dung = fields.Date(
        string='Ngày bắt đầu sử dụng',
        help='Ngày bắt đầu tính khấu hao (có thể khác ngày mua)'
    )
    thoi_gian_khau_hao = fields.Integer(string='Thời gian khấu hao (năm)', default=5, help='Số năm khấu hao tài sản')
    
    # Phương pháp khấu hao
    phuong_phap_khau_hao = fields.Selection([
        ('duong_thang', 'Đường thẳng (Straight-line)'),
        ('so_du_giam_dan', 'Số dư giảm dần (Declining balance)'),
        ('tong_so_nam', 'Tổng số năm (Sum-of-years)'),
    ], string='Phương pháp khấu hao', default='duong_thang', required=True, tracking=True)
    
    ty_le_khau_hao_nam = fields.Float(
        string='Tỷ lệ khấu hao (%/năm)',
        compute='_compute_ty_le_khau_hao',
        store=True,
        help='Tỷ lệ khấu hao hàng năm'
    )
    
    # Giá trị khấu hao
    gia_tri_khau_hao_hang_thang = fields.Float(
        string='Khấu hao hàng tháng',
        compute='_compute_khau_hao',
        store=True
    )
    gia_tri_khau_hao_hang_nam = fields.Float(
        string='Khấu hao hàng năm',
        compute='_compute_khau_hao',
        store=True
    )
    tong_gia_tri_da_khau_hao = fields.Float(
        string='Tổng đã khấu hao',
        compute='_compute_khau_hao',
        store=True,
        help='Tổng giá trị đã khấu hao đến hiện tại'
    )
    gia_tri_con_lai = fields.Float(
        string='Giá trị còn lại',
        compute='_compute_khau_hao',
        store=True
    )
    ty_le_khau_hao_hoan_thanh = fields.Float(
        string='% Khấu hao hoàn thành',
        compute='_compute_khau_hao',
        store=True
    )
    
    # Trạng thái
    tinh_trang = fields.Selection([
        ('moi', 'Mới 100%'),
        ('tot', 'Đang sử dụng tốt'),
        ('trung_binh', 'Đang sử dụng (có vấn đề nhỏ)'),
        ('can_bao_tri', 'Cần bảo trì'),
        ('hong', 'Hỏng'),
        ('cho_thanh_ly', 'Chờ thanh lý'),
        ('da_thanh_ly', 'Đã thanh lý'),
    ], string='Tình trạng', default='moi', required=True, tracking=True)
    
    vi_tri = fields.Selection([
        ('kho', 'Kho'),
        ('dang_su_dung', 'Đang sử dụng'),
        ('bao_tri', 'Bảo trì'),
        ('thanh_ly', 'Thanh lý'),
    ], string='Vị trí', default='kho', required=True, tracking=True)
    
    # Thông tin chi tiết
    mo_ta = fields.Text(string='Mô tả chi tiết')
    ghi_chu = fields.Text(string='Ghi chú')
    hinh_anh = fields.Binary(string='Hình ảnh')
    
    # QR Code & Barcode
    qr_code = fields.Binary(
        string='QR Code',
        compute='_compute_qr_code',
        store=False,
        help='QR code để quét nhanh thông tin tài sản'
    )
    barcode = fields.Char(
        string='Barcode',
        copy=False,
        help='Mã vạch để quét bằng máy scanner'
    )
    
    # LIÊN KẾT VỚI MODULE KHÁC
    phong_ban_id = fields.Many2one(
        'phong_ban',
        string='Phòng ban',
        tracking=True,
        help='Phòng ban đang quản lý/sử dụng tài sản'
    )
    nguoi_quan_ly_id = fields.Many2one(
        'nhan_vien',
        string='Người quản lý',
        tracking=True,
        help='Nhân viên chịu trách nhiệm quản lý tài sản này'
    )
    phong_hop_id = fields.Many2one(
        'quan_ly_phong_hop',
        string='Phòng họp',
        tracking=True,
        help='Chỉ áp dụng cho thiết bị phòng họp'
    )
    
    # QUAN HỆ ONE2MANY
    lich_su_su_dung_ids = fields.One2many(
        'lich_su_su_dung_tai_san',
        'tai_san_id',
        string='Lịch sử sử dụng'
    )
    lich_su_bao_tri_ids = fields.One2many(
        'bao_tri_tai_san',
        'tai_san_id',
        string='Lịch sử bảo trì'
    )
    lich_su_chuyen_giao_ids = fields.One2many(
        'chuyen_giao_tai_san',
        'tai_san_id',
        string='Lịch sử chuyển giao'
    )
    
    # Computed fields
    so_lan_bao_tri = fields.Integer(
        string='Số lần bảo trì',
        compute='_compute_so_lan_bao_tri'
    )
    tong_chi_phi_bao_tri = fields.Float(
        string='Tổng chi phí bảo trì',
        compute='_compute_tong_chi_phi_bao_tri'
    )
    nguoi_dang_su_dung = fields.Many2one(
        'nhan_vien',
        string='Người đang sử dụng',
        compute='_compute_nguoi_dang_su_dung'
    )

    @api.model
    def create(self, vals):
        """Tự động tạo mã tài sản"""
        if vals.get('ma_tai_san', 'New') == 'New':
            vals['ma_tai_san'] = self.env['ir.sequence'].next_by_code('tai_san.sequence') or 'New'
        return super(TaiSan, self).create(vals)

    def write(self, vals):
        """Tự động tạo lịch sử sử dụng khi vi_tri đổi sang 'dang_su_dung'"""
        result = super(TaiSan, self).write(vals)
        
        # Nếu vị trí đổi thành "Đang sử dụng"
        if vals.get('vi_tri') == 'dang_su_dung':
            for record in self:
                # Kiểm tra xem có lịch sử đang sử dụng chưa hoàn thành không
                lich_su_dang_mo = record.lich_su_su_dung_ids.filtered(lambda r: r.trang_thai == 'dang_su_dung')
                
                # Chỉ tạo mới nếu chưa có lịch sử đang mở
                if not lich_su_dang_mo:
                    # Tạo lịch sử sử dụng mới
                    self.env['lich_su_su_dung_tai_san'].create({
                        'tai_san_id': record.id,
                        'nguoi_su_dung_id': record.nguoi_quan_ly_id.id if record.nguoi_quan_ly_id else False,
                        'phong_ban_id': record.phong_ban_id.id if record.phong_ban_id else False,
                        'ngay_bat_dau': fields.Date.today(),
                        'trang_thai': 'dang_su_dung',
                    })
        
        # Nếu vị trí đổi về "Kho" → tự động trả tài sản
        elif vals.get('vi_tri') == 'kho':
            for record in self:
                # Tìm các lịch sử đang sử dụng và đóng lại
                lich_su_dang_mo = record.lich_su_su_dung_ids.filtered(lambda r: r.trang_thai == 'dang_su_dung')
                for lich_su in lich_su_dang_mo:
                    lich_su.write({
                        'trang_thai': 'da_tra',
                        'ngay_ket_thuc': fields.Date.today(),
                    })
        
        return result

    @api.depends('gia_tri', 'ngay_mua', 'ngay_bat_dau_su_dung', 'thoi_gian_khau_hao', 'phuong_phap_khau_hao', 'gia_tri_thanh_ly')
    def _compute_khau_hao(self):
        """Tính toán khấu hao tài sản theo nhiều phương pháp"""
        for record in self:
            if record.thoi_gian_khau_hao <= 0:
                record.gia_tri_khau_hao_hang_thang = 0
                record.gia_tri_khau_hao_hang_nam = 0
                record.tong_gia_tri_da_khau_hao = 0
                record.gia_tri_con_lai = record.gia_tri
                record.ty_le_khau_hao_hoan_thanh = 0
                continue
            
            # Ngày bắt đầu tính khấu hao
            ngay_tinh = record.ngay_bat_dau_su_dung or record.ngay_mua
            if not ngay_tinh:
                record.gia_tri_khau_hao_hang_thang = 0
                record.gia_tri_khau_hao_hang_nam = 0
                record.tong_gia_tri_da_khau_hao = 0
                record.gia_tri_con_lai = record.gia_tri
                record.ty_le_khau_hao_hoan_thanh = 0
                continue
            
            # Tính số tháng đã sử dụng
            today = date.today()
            months_used = (today.year - ngay_tinh.year) * 12 + (today.month - ngay_tinh.month)
            months_used = max(0, months_used)  # Không âm
            
            # Giá trị có thể khấu hao
            gia_tri_co_the_khau_hao = record.gia_tri - record.gia_tri_thanh_ly
            
            # Tính khấu hao theo phương pháp
            if record.phuong_phap_khau_hao == 'duong_thang':
                # Phương pháp đường thẳng (Straight-line)
                record.gia_tri_khau_hao_hang_nam = gia_tri_co_the_khau_hao / record.thoi_gian_khau_hao
                record.gia_tri_khau_hao_hang_thang = record.gia_tri_khau_hao_hang_nam / 12
                record.tong_gia_tri_da_khau_hao = record.gia_tri_khau_hao_hang_thang * months_used
                
            elif record.phuong_phap_khau_hao == 'so_du_giam_dan':
                # Phương pháp số dư giảm dần (Declining balance - Double declining)
                # Tỷ lệ = 2 / Thời gian khấu hao
                ty_le = 2.0 / record.thoi_gian_khau_hao
                
                # Tính khấu hao lũy kế theo từng năm
                gia_tri_hien_tai = record.gia_tri
                tong_khau_hao = 0
                years_passed = months_used // 12
                months_in_current_year = months_used % 12
                
                for year in range(years_passed):
                    khau_hao_nam = gia_tri_hien_tai * ty_le
                    # Không khấu hao quá giá trị có thể khấu hao
                    khau_hao_nam = min(khau_hao_nam, gia_tri_hien_tai - record.gia_tri_thanh_ly)
                    tong_khau_hao += khau_hao_nam
                    gia_tri_hien_tai -= khau_hao_nam
                
                # Tính khấu hao năm hiện tại
                khau_hao_nam_hien_tai = gia_tri_hien_tai * ty_le
                khau_hao_nam_hien_tai = min(khau_hao_nam_hien_tai, gia_tri_hien_tai - record.gia_tri_thanh_ly)
                record.gia_tri_khau_hao_hang_nam = khau_hao_nam_hien_tai
                record.gia_tri_khau_hao_hang_thang = khau_hao_nam_hien_tai / 12
                
                # Cộng khấu hao các tháng trong năm hiện tại
                tong_khau_hao += (khau_hao_nam_hien_tai / 12) * months_in_current_year
                record.tong_gia_tri_da_khau_hao = tong_khau_hao
                
            elif record.phuong_phap_khau_hao == 'tong_so_nam':
                # Phương pháp tổng số năm (Sum-of-years' digits)
                # Tổng số năm = n(n+1)/2
                tong_so_nam = (record.thoi_gian_khau_hao * (record.thoi_gian_khau_hao + 1)) / 2
                
                # Tính khấu hao lũy kế
                tong_khau_hao = 0
                years_passed = months_used // 12
                months_in_current_year = months_used % 12
                
                for year in range(years_passed):
                    so_nam_con_lai = record.thoi_gian_khau_hao - year
                    khau_hao_nam = (so_nam_con_lai / tong_so_nam) * gia_tri_co_the_khau_hao
                    tong_khau_hao += khau_hao_nam
                
                # Tính khấu hao năm hiện tại
                so_nam_con_lai = record.thoi_gian_khau_hao - years_passed
                khau_hao_nam_hien_tai = (so_nam_con_lai / tong_so_nam) * gia_tri_co_the_khau_hao
                record.gia_tri_khau_hao_hang_nam = khau_hao_nam_hien_tai
                record.gia_tri_khau_hao_hang_thang = khau_hao_nam_hien_tai / 12
                
                # Cộng khấu hao các tháng trong năm hiện tại
                tong_khau_hao += (khau_hao_nam_hien_tai / 12) * months_in_current_year
                record.tong_gia_tri_da_khau_hao = tong_khau_hao
            
            # Đảm bảo không khấu hao quá giá trị có thể khấu hao
            record.tong_gia_tri_da_khau_hao = min(record.tong_gia_tri_da_khau_hao, gia_tri_co_the_khau_hao)
            
            # Giá trị còn lại
            record.gia_tri_con_lai = max(record.gia_tri_thanh_ly, record.gia_tri - record.tong_gia_tri_da_khau_hao)
            
            # Tỷ lệ khấu hao hoàn thành
            if gia_tri_co_the_khau_hao > 0:
                record.ty_le_khau_hao_hoan_thanh = (record.tong_gia_tri_da_khau_hao / gia_tri_co_the_khau_hao) * 100
            else:
                record.ty_le_khau_hao_hoan_thanh = 0
    
    @api.depends('thoi_gian_khau_hao', 'phuong_phap_khau_hao')
    def _compute_ty_le_khau_hao(self):
        """Tính tỷ lệ khấu hao hàng năm"""
        for record in self:
            if record.thoi_gian_khau_hao > 0:
                if record.phuong_phap_khau_hao == 'duong_thang':
                    record.ty_le_khau_hao_nam = (1.0 / record.thoi_gian_khau_hao) * 100
                elif record.phuong_phap_khau_hao == 'so_du_giam_dan':
                    record.ty_le_khau_hao_nam = (2.0 / record.thoi_gian_khau_hao) * 100
                else:
                    record.ty_le_khau_hao_nam = 0  # Tỷ lệ thay đổi theo năm
            else:
                record.ty_le_khau_hao_nam = 0
    
    @api.depends('ma_tai_san', 'name')
    def _compute_qr_code(self):
        """Tạo QR code tự động cho tài sản"""
        try:
            import qrcode
            import base64
            from io import BytesIO
            
            for record in self:
                if record.ma_tai_san and record.ma_tai_san != 'New':
                    # Tạo URL hoặc thông tin tài sản
                    base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
                    tai_san_url = f"{base_url}/web#id={record.id}&model=tai_san&view_type=form"
                    
                    # Tạo QR code
                    qr = qrcode.QRCode(
                        version=1,
                        error_correction=qrcode.constants.ERROR_CORRECT_L,
                        box_size=10,
                        border=4,
                    )
                    qr.add_data(tai_san_url)
                    qr.make(fit=True)
                    
                    # Chuyển thành hình ảnh
                    img = qr.make_image(fill_color="black", back_color="white")
                    buffer = BytesIO()
                    img.save(buffer, format='PNG')
                    record.qr_code = base64.b64encode(buffer.getvalue())
                else:
                    record.qr_code = False
        except ImportError:
            # Nếu không có thư viện qrcode, bỏ qua
            for record in self:
                record.qr_code = False

    @api.depends('lich_su_bao_tri_ids')
    def _compute_so_lan_bao_tri(self):
        """Đếm số lần bảo trì"""
        for record in self:
            record.so_lan_bao_tri = len(record.lich_su_bao_tri_ids.filtered(lambda r: r.trang_thai == 'hoan_thanh'))

    @api.depends('lich_su_bao_tri_ids.chi_phi')
    def _compute_tong_chi_phi_bao_tri(self):
        """Tính tổng chi phí bảo trì"""
        for record in self:
            record.tong_chi_phi_bao_tri = sum(record.lich_su_bao_tri_ids.mapped('chi_phi'))

    @api.depends('lich_su_su_dung_ids.trang_thai')
    def _compute_nguoi_dang_su_dung(self):
        """Tìm người đang sử dụng tài sản"""
        for record in self:
            dang_su_dung = record.lich_su_su_dung_ids.filtered(lambda r: r.trang_thai == 'dang_su_dung')
            record.nguoi_dang_su_dung = dang_su_dung[0].nguoi_su_dung_id if dang_su_dung else False

    def action_cap_nhat_tinh_trang(self):
        """Mở wizard cập nhật tình trạng"""
        return {
            'type': 'ir.actions.act_window',
            'name': 'Cập nhật tình trạng',
            'res_model': 'tai_san',
            'res_id': self.id,
            'view_mode': 'form',
            'target': 'new',
        }

    def action_bao_tri(self):
        """Tạo phiếu bảo trì mới"""
        return {
            'type': 'ir.actions.act_window',
            'name': 'Tạo phiếu bảo trì',
            'res_model': 'bao_tri_tai_san',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_tai_san_id': self.id,
            }
        }

    def action_chuyen_giao(self):
        """Tạo phiếu chuyển giao"""
        return {
            'type': 'ir.actions.act_window',
            'name': 'Chuyển giao tài sản',
            'res_model': 'chuyen_giao_tai_san',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_tai_san_id': self.id,
                'default_tu_phong_ban_id': self.phong_ban_id.id,
                'default_tu_nguoi_id': self.nguoi_quan_ly_id.id,
            }
        }
