# -*- coding: utf-8 -*-
{
    'name': "HR Attendance Face Recognition",

    'summary': """Employee Attendance using Face Recognition""",

    'description': """
        This module will help you to convert your normal attendance  system to facial recognition attendance system.
        To use module you have to configure the employees images only, those images will be used for face recognition.
        This app is capable to work with large databases.
        HR Attendance
        
    """,

    'author': 'ErpMstar Solutions',
    'category': 'Human Resources/Attendances',
    'version': '1.0',

    # any module necessary for this one to work correctly
    'depends': ['hr_attendance', 'web_widget_image_cam'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'security/attendance_security.xml',
        'views/views.xml',
        'views/templates.xml',
        'views/res_config_settings_views.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
    ],

    'assets': {
        'hr_attendance.assets_public_attendance': [
              'web/static/lib/jquery/jquery.js',
            'web/static/lib/popper/popper.js',
            'web/static/lib/bootstrap/js/dist/dom/data.js',
            'web/static/lib/bootstrap/js/dist/dom/event-handler.js',
            'web/static/lib/bootstrap/js/dist/dom/manipulator.js',
            'web/static/lib/bootstrap/js/dist/dom/selector-engine.js',
            'web/static/lib/bootstrap/js/dist/base-component.js',
            'web/static/lib/bootstrap/js/dist/alert.js',
            'web/static/lib/bootstrap/js/dist/button.js',
            'web/static/lib/bootstrap/js/dist/carousel.js',
            'web/static/lib/bootstrap/js/dist/collapse.js',
            'web/static/lib/bootstrap/js/dist/dropdown.js',
            'web/static/lib/bootstrap/js/dist/modal.js',
            'web/static/lib/bootstrap/js/dist/offcanvas.js',
            'web/static/lib/bootstrap/js/dist/tooltip.js',
            'web/static/lib/bootstrap/js/dist/popover.js',
            'web/static/lib/bootstrap/js/dist/scrollspy.js',
            'web/static/lib/bootstrap/js/dist/tab.js',
            'web/static/lib/bootstrap/js/dist/toast.js',
            'web/static/src/legacy/js/libs/bootstrap.js',
            'web/static/src/legacy/js/libs/jquery.js',


            '/face_recognition_hr_attendance/static/src/js/face-api.min.js',
            '/face_recognition_hr_attendance/static/src/js/face_attendance_py_implementation.js',
            '/face_recognition_hr_attendance/static/src/xml/*.xml',
        ],
        # 'web.assets_qweb': [
        #     '/face_recognition_hr_attendance/static/src/xml/*.xml',
        # ],
    },
    'installable': True,
    'auto_install': False,
    'application': True,
    'external_dependencies': {
        'python': ['cmake', 'dlib', 'face_recognition', 'numpy', 'opencv-python'],
    },
    'images': ['static/description/banner.jpg'],
    'price': 120,
    'currency': 'EUR',
}
