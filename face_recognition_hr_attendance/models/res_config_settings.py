# -*- coding: utf-8 -*-

import base64
import io
import pickle
from pickle import _Pickler

import cv2
import face_recognition
import numpy as np

from odoo import models, fields, api
from odoo.exceptions import ValidationError


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    file_path = fields.Text("Encoding File Path")
    # group_attendance_use_badge = fields.Boolean(string='Employee Badge Scan',
    #                                             implied_group="face_recognition_hr_attendance.group_hr_attendance_use_badge")
    # group_attendance_use_manual = fields.Boolean(string='Employee Manual Identification',
    #                                              implied_group="face_recognition_hr_attendance.group_hr_attendance_use_manual")
    # group_attendance_use_face = fields.Boolean(string='Employee Face Recognition',
    #                                            implied_group="face_recognition_hr_attendance.group_hr_attendance_use_face")
    #
    # group_attendance_use_timer = fields.Boolean(string='Employee Face Recognition Fail: User Timer',
    #                                             implied_group="face_recognition_hr_attendance.group_hr_attendance_use_timer")

    def set_values(self):
        res = super(ResConfigSettings, self).set_values()
        self.env['ir.config_parameter'].set_param(
            'face_recognition_hr_attendance.file_path', self.file_path)
        return res

    @api.model
    def get_values(self):
        res = super(ResConfigSettings, self).get_values()
        ICPSudo = self.env['ir.config_parameter'].sudo()
        file_path = ICPSudo.get_param(
            'face_recognition_hr_attendance.file_path')

        res.update(
            file_path=file_path,
        )
        return res

    def save_encodings(self):
        employee_ids = self.env["hr.employee"].search(
            [("attendance_image_ids", "!=", False), ("barcode", "!=", False)])
        known_encodings = []
        known_names = []
        for emp_id in employee_ids:
            for emp_img_id in emp_id.attendance_image_ids:
                image_stream = io.BytesIO(
                    base64.b64decode(emp_img_id.image_data))
                image_stream.seek(0)
                file_bytes = np.asarray(
                    bytearray(image_stream.read()), dtype=np.uint8)
                img = cv2.imdecode(file_bytes, cv2.IMREAD_COLOR)
                boxes = face_recognition.face_locations(img, model="hog")
                encodings = face_recognition.face_encodings(img, boxes)
                for encoding in encodings:
                    known_encodings.append(encoding)
                    known_names.append(emp_id.id)

        data = {"encodings": known_encodings, "names": known_names}
        ICPSudo = self.env['ir.config_parameter'].sudo()
        stream = io.BytesIO()
        _Pickler(stream).dump(data)
        stream.seek(0)
        output = base64.encodebytes(stream.read())
        print("data", data)
        self.company_id.encoded_image_file = output
        print("self.company_id", self.company_id)

        # a = pickle.loads(self.company_id.encoded_image_file)
        image_stream = io.BytesIO(base64.b64decode(self.company_id.encoded_image_file))
        image_stream.seek(0)
        a = pickle.loads(image_stream.read())

        print("a",a)
        # file_path = ICPSudo.get_param(
        #     'face_recognition_hr_attendance.file_path')
        # if file_path:
        #     f = open(file_path + "/encodings.pickle", "wb")
        #     f.write(pickle.dumps(data))
        #     f.close()
        # else:
        #     raise ValidationError("Set Encoding File Path!")
