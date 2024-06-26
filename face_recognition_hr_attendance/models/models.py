# -*- coding: utf-8 -*-
import base64
import io
import json
import os
import pickle

import cv2
import face_recognition
import face_recognition as fr
import numpy as np

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class EmpImages(models.Model):
    _name = "hr.employee.image"

    name = fields.Char(required=True)
    image_data = fields.Image(required=True)
    employee_id = fields.Many2one("hr.employee")

    @api.onchange("image_data")
    def validate_img(self):
        if self.image_data:
            ICPSudo = self.env['ir.config_parameter'].sudo()
            # file_path = ICPSudo.get_param(
            #     'face_recognition_hr_attendance.file_path')
            # if file_path:
            cv2_base_dir = os.path.dirname(os.path.abspath(cv2.__file__))
            haar_model = os.path.join(cv2_base_dir, 'data/haarcascade_frontalface_default.xml')

            # cv2.CascadeClassifier(cv2.)
            # face_cascade = cv2.CascadeClassifier(
            #     file_path + '/haarcascade_frontalface_default.xml')

            face_cascade = cv2.CascadeClassifier(haar_model)
            image_stream = io.BytesIO(base64.b64decode(self.image_data))
            image_stream.seek(0)
            file_bytes = np.asarray(
                bytearray(image_stream.read()), dtype=np.uint8)
            img = cv2.imdecode(file_bytes, cv2.COLOR_BGR2GRAY)
            faces = face_cascade.detectMultiScale(img, 1.1, 4)
            if len(faces) < 1:
                raise ValidationError(
                    "Selected image do not have any human face! Add a correct image.")
            # else:
            #     raise ValidationError("Set Encoding File Path!")


class HrEmployee(models.Model):
    _inherit = "hr.employee"

    attendance_image_ids = fields.One2many("hr.employee.image", "employee_id")

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
        file_path = ICPSudo.get_param(
            'face_recognition_hr_attendance.file_path')
        if file_path:
            f = open(file_path + "/encodings.pickle", "wb")
            f.write(pickle.dumps(data))
            f.close()
        else:
            raise ValidationError("Set Encoding File Path!")

    @api.model
    def get_emp_img_data(self):
        emp_ids = self.search(
            [("attendance_image_ids", "!=", False), ("barcode", "!=", False)])

        emp_ids_only = []
        emp_data = []
        for emp_id in emp_ids:
            emp_data.append({
                "emp_id": emp_id.id,
                "name": emp_id.name,
                "img_ids": emp_id.attendance_image_ids.ids,
                "barcode": emp_id.barcode,
            })
            emp_ids_only.append(emp_id.id)
        return json.dumps({"emp_data": emp_data, "emp_ids_only": emp_ids_only})

    @api.model
    def attendance_scan(self, barcode, img=None):
        """ Receive a barcode scanned from the Kiosk Mode and change the attendances of corresponding employee.
            Returns either an action or a warning.
        """
        employee = self.sudo().search([('barcode', '=', barcode)], limit=1)
        if employee:
            result = employee._attendance_action(
                'hr_attendance.hr_attendance_action_kiosk_mode')
            action = result.get("action")
            if img and not isinstance(img, dict):
                img_str = img.split(",", 1)
                if len(img_str) == 2:
                    img_base64 = img_str[1].encode()
                    attendance = action.get("attendance")
                    if attendance:
                        attendance_id = attendance.get("id")
                        attendance_id = self.env["hr.attendance"].browse(
                            attendance_id)
                        attendance_id.attendance_by = "facial_recognition"
                        if not attendance_id.check_in_image and not attendance_id.check_out_image:
                            attendance_id.check_in_image = img_base64
                        elif attendance_id.check_in_image and not attendance_id.check_out_image:
                            attendance_id.check_out_image = img_base64

            return result
        return {'warning': _('No employee corresponding to barcode %(barcode)s') % {'barcode': barcode}}


class HrAttendance(models.Model):
    _inherit = "hr.attendance"

    attendance_by = fields.Selection([("other", "Other"), ("facial_recognition", "Facial Recognition")],
                                     default="other", string="Attendance Mode")
    check_in_image = fields.Image()
    check_out_image = fields.Image()


class ResCompany(models.Model):
    _inherit = "res.company"

    attendance_kiosk_mode = fields.Selection(selection_add=[("facial_recognition", "Facial Recognition")],
                                             string='Attendance Mode', default='barcode_manual')
    encoded_image_file = fields.Binary()