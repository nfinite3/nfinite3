# -*- coding: utf-8 -*-
import base64
import io
import json
import pickle
import sys

import cv2
import face_recognition
import numpy as np

from odoo.addons.hr_attendance.controllers.main import HrAttendance
from odoo import http
from odoo.exceptions import ValidationError
from odoo.http import request
import logging

_logger = logging.getLogger(__name__)


class FaceRecognitionHrAttendance(http.Controller):
    @staticmethod
    def _get_company(token):
        company = request.env['res.company'].sudo().search([('attendance_kiosk_key', '=', token)])
        return company

    @http.route('/emp/attendance/img', type='http', auth="none", methods=['POST'], csrf=False)
    def index(self, **kw):
        img = kw.get("img")
        token = kw.get("token")
        names = []
        if img:
            img_str = img.split(",", 1)
            if len(img_str) == 2:
                img_base64 = img_str[1].encode()
                names = self.classify_face(img_base64, token)
        if len(names) == 1 and isinstance(names[0], int):
            emp_id = http.request.env["hr.employee"].sudo().browse(names)
            print("Emp ID", emp_id, emp_id.name, emp_id.barcode)
            if emp_id.barcode:
                return json.dumps({"name": emp_id.name, "barcode": emp_id.barcode})
            else:
                return json.dumps({"error": "No match found! Scan your face again or Contact admin."})
        elif len(names) > 1:
            return json.dumps({"error": "Multiple match found! Scan your face again."})
        else:
            return json.dumps({"error": "No match found! Scan your face again or Contact admin."})

    def classify_face(self, unknown_img, token):
        # data = None
        ICPSudo = request.env['ir.config_parameter'].sudo()
        file_path = ICPSudo.get_param('face_recognition_hr_attendance.file_path')
        # if file_path:
        #     try:
        #         data = pickle.loads(open(file_path + "/encodings.pickle", "rb").read())
        #     except OSError as err:
        #         _logger.error("Could not open/read file: encodings.pickle %s" % err)
        #         raise ValidationError("Could not open/read file: encodings.pickle %s" % err)
        # else:
        #     raise ValidationError("Set Encoding File Path!")
        # company_id = request.env.user.company_id
        # print("company_id", request.env.company, token)
        company = self._get_company(token)

        data_stream = io.BytesIO(base64.b64decode(company.encoded_image_file))
        data_stream.seek(0)
        data = pickle.loads(data_stream.read())
        image_stream = io.BytesIO(base64.b64decode(unknown_img))
        image_stream.seek(0)
        file_bytes = np.asarray(bytearray(image_stream.read()), dtype=np.uint8)
        img = cv2.imdecode(file_bytes, cv2.COLOR_BGR2GRAY)
        face_locations = face_recognition.face_locations(img)
        unknown_face_encodings = face_recognition.face_encodings(img, face_locations)

        face_names = []
        names = []
        for face_encoding in unknown_face_encodings:
            matches = face_recognition.compare_faces(data["encodings"], face_encoding)
            name = "Unknown"
            face_distances = face_recognition.face_distance(data["encodings"], face_encoding)
            best_match_index = np.argmin(face_distances)
            if matches[best_match_index]:
                name = data["names"][best_match_index]

            names.append(name)
        return names


class HrAttendanceFacial(HrAttendance):
    @http.route('/hr_attendance/attendance_barcode_scanned', type="json", auth="public")
    def scan_barcode(self, token, barcode, img=None):
        company = self._get_company(token)
        if company:
            employee = request.env['hr.employee'].sudo().search(
                [('barcode', '=', barcode), ('company_id', '=', company.id)], limit=1)
            if employee:
                attendance_id = employee._attendance_action_change(self._get_geoip_response('kiosk'))
                if img and not isinstance(img, dict) and attendance_id:
                    img_str = img.split(",", 1)
                    if len(img_str) == 2:
                        img_base64 = img_str[1].encode()
                        attendance_id.attendance_by = "facial_recognition"
                        if not attendance_id.check_in_image and not attendance_id.check_out_image:
                            attendance_id.check_in_image = img_base64
                        elif attendance_id.check_in_image and not attendance_id.check_out_image:
                            attendance_id.check_out_image = img_base64

                return self._get_employee_info_response(employee)
        return {}
