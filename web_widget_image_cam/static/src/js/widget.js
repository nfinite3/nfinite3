/** @odoo-module */

import { patch } from "@web/core/utils/patch";

import { ImageField, imageField } from '@web/views/fields/image/image_field';
import Dialog from '@web/legacy/js/core/dialog';


patch(ImageField.prototype, {

    onCaptureImage() {
        var self = this

        var CameraDialog = ` <div><div class="container-fluid">
                                <div class="row" style="text-align: center;">
                                    <div class="col-md-5">
                                        <span class="live_cam_img"/>
                                    </div>
                                    <div class="col-md-2"></div>
                                    <div class="col-md-5">
                                        <span class="webcam_img"/>
                                    </div>
                                </div>
                            </div></div>`
        Webcam.set({
            width: 320,
            height: 240,
            image_format: 'jpeg',
            jpeg_quality: 100,
            force_flash: false,
            fps: 30,
            flip_horiz: false,
        });
        var img_data
        var dialog = new Dialog(this, Object.assign({
            size: 'large',
            dialogClass: 'o_act_window',
            title: "Camera",
            $content: CameraDialog,
            buttons: [
                {
                    text: "Capture Image", classes: 'btn-primary',
                    click: function () {
                        Webcam.snap(function (data) {
                            img_data = data;
                            $(".webcam_img").html('<img src="' + img_data + '"/>');
                        });
                        if (Webcam.live) {
                            $('.save_close_btn').removeAttr('disabled');
                        }
                    }
                },
                {
                    text: "Save & Close", classes: 'btn-primary save_close_btn', close: true,
                    click: function () {
                        var img_data_base64 = img_data.split(',')[1];
                        var approx_img_size = 3 * (img_data_base64.length / 4) - (img_data_base64.match(/=+$/g) || []).length;
                        self.onFileUploaded({
                            name: "web-cam-preview.jpeg",
                            size: approx_img_size,
                            type: "image/jpeg",
                            data: img_data_base64,
                        })
                    }
                },
                {
                    text: "Close", close: true
                }
            ]
        }))
        dialog.open();
        dialog.opened().then(function () {
            Webcam.attach('.live_cam_img');
            $('.save_close_btn').attr('disabled', 'disabled');
            $(".webcam_img").html('<img src="/web/static/img/placeholder.png"/>');
        });
    }
})

patch(Dialog.prototype, {
    close: function () {
        Webcam.reset();
        this.destroy();
    },
})




