# -*- coding: utf-8 -*-
{
    'name': "nhan_su",

    'summary': """
        Quản lý nhân sự toàn diện với vai trò nghiệp vụ, phân quyền, 
        quản lý tài sản, mượn trả thiết bị, vi phạm và nhật ký hoạt động""",

    'description': """
        Module quản lý nhân sự mở rộng bao gồm:
        - Quản lý vai trò nghiệp vụ (HR Role)
        - Trạng thái làm việc và phân quyền
        - Quản lý trưởng đơn vị và phê duyệt
        - Quyền đặt phòng họp với hạn mức
        - Tham gia cuộc họp
        - Phân công tài sản
        - Mượn trả thiết bị với workflow
        - Nhật ký sử dụng tài nguyên
        - Quản lý vi phạm nhân sự
        - Báo cáo và thống kê
    """,

    'author': "My Company",
    'website': "http://www.yourcompany.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/15.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.2',

    # any module necessary for this one to work correctly
    'depends': ['base', 'mail'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'data/sequence.xml',
        'views/chuc_vu.xml',
        'views/don_vi.xml',
        'views/phong_ban.xml',
        'views/nhan_vien.xml',
        'views/lich_su_cong_tac.xml',
        'views/chung_chi_bang_cap.xml',
        'views/danh_sach_chung_chi_bang_cap.xml',
        'views/hr_role.xml',
        'views/menu.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}
