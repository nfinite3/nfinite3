/** @odoo-module **/

// import { session } from "@web/session";
import { patch } from "@web/core/utils/patch";
import kioskAttendanceApp from "@hr_attendance/public_kiosk/public_kiosk_app"
import { onWillStart } from "@odoo/owl";
import { useService } from '@web/core/utils/hooks';

// var cam_feed = 0
// var video
// var canvas
var employee_data
// var canvas = document.getElementById('cam_canvas')
var labeledFaceDescriptors
var timerId = []
var interval = []
var video
var canvas = document.getElementById('cam_canvas')
var canvas_photo = document.getElementById('canvas_photo')
var photo = document.getElementById('photo');
var attandance_app
var window_width
var window_height


patch(kioskAttendanceApp.kioskAttendanceApp.prototype, {

    setup() {
        timerId.forEach((inter => {
            clearInterval(inter)
        }));

        var self = this;
        attandance_app = this
        this.user = useService("user");
        onWillStart(async () => {
            if (this.props.kioskMode === 'facial_recognition') {

                Promise.all([
                    faceapi.nets.tinyFaceDetector.loadFromUri('/face_recognition_hr_attendance/static/src/assets/models'),
                    faceapi.nets.faceLandmark68Net.loadFromUri('/face_recognition_hr_attendance/static/src/assets/models'),
                    // faceapi.nets.faceRecognitionNet.loadFromUri('/face_recognition_hr_attendance/static/src/assets/models'),
                    // faceapi.nets.ssdMobilenetv1.loadFromUri('/face_recognition_hr_attendance/static/src/assets/models'),
                    faceapi.nets.faceExpressionNet.loadFromUri('/face_recognition_hr_attendance/static/src/assets/models'),
                ]).then(function () {
                    // $("#stop_video").click(self._stopVideo)
                    console.log("Loaded...")
                });
            }
        });
        super.setup()
    },

    prepareScan() {
        timerId.forEach((inter => {
            clearInterval(inter)
        }));
        photo.setAttribute('src', "#");
        photo = document.getElementById('photo');
        $("#video_box").show()
        $("#loader_img").show()
        $("#error_message").hide()
        $("#scan_again").hide()

    },

    startCam() {
        window_width = window.innerWidth
        window_height = window.innerHeight
        // clearInterval(timerId);
        timerId.forEach((inter => {
            clearInterval(inter)
        }));
        var self = attandance_app

        video = document.getElementById('video')
        canvas = document.getElementById('cam_canvas')
        canvas_photo = document.getElementById('canvas_photo')
        photo = document.getElementById('photo');

        if (window_width >= 768) {
            video.setAttribute("width", 647)
            video.setAttribute("height", 486)

            canvas.setAttribute("width", 647)
            canvas.setAttribute("height", 486)

            canvas_photo.setAttribute("width", 647)
            canvas_photo.setAttribute("height", 486)
        }
        else if (window_width >= 425) {
            video.setAttribute("width", 400)
            video.setAttribute("height", 300)

            canvas.setAttribute("width", 400)
            canvas.setAttribute("height", 300)

            canvas_photo.setAttribute("width", 400)
            canvas_photo.setAttribute("height", 300)
        }
        else if (window_width >= 375) {
            video.setAttribute("width", 350)
            video.setAttribute("height", 300)

            canvas.setAttribute("width", 350)
            canvas.setAttribute("height", 300)

            canvas_photo.setAttribute("width", 350)
            canvas_photo.setAttribute("height", 300)
        }

        else if (window_width >= 320) {
            video.setAttribute("width", 300)
            video.setAttribute("height", 250)

            canvas.setAttribute("width", 300)
            canvas.setAttribute("height", 250)

            canvas_photo.setAttribute("width", 300)
            canvas_photo.setAttribute("height", 250)
        }

        photo.setAttribute('src', "#");

        startVideo()
        $("#video_box").show()
        $("#loader_img").show()
        $("#error_message").hide()
        $("#scan_again").hide()

        function startVideo() {
            $("#web_cam_error").hide()
            navigator.getUserMedia = (
                navigator.getUserMedia ||
                navigator.webkitGetUserMedia ||
                navigator.mozGetUserMedia ||
                navigator.msGetUserMedia
            );
            navigator.getUserMedia(
                { video: {} },
                stream => video.srcObject = stream,
                err => {
                    console.error(err)
                    $("#web_cam_error").show()
                }
            )
        }



        function clearphoto() {
            var context = canvas_photo.getContext('2d');
            context.fillStyle = "#AAA";
            context.fillRect(0, 0, canvas_photo.width, canvas_photo.height);

            var data = canvas_photo.toDataURL('image/png');
            photo.setAttribute('src', data);
        }

        async function takepicture() {
            var context = canvas_photo.getContext('2d');
            if (video.width && video.height) {
                canvas_photo.width = video.width;
                canvas_photo.height = video.height;
                context.drawImage(video, 0, 0, video.width, video.height);
                var data = canvas_photo.toDataURL('image/png');
                photo.setAttribute('src', data);
                if ($("#photo").attr("src") != "#") {
                    // $("#video_box").hide()
                    // $("#success_box").show()
                    // recognizeImage()
                    $.ajax({
                        type: "POST",
                        url: "/emp/attendance/img",
                        data: { "img": $("#photo").attr("src"), "token": self.props.token },
                        success: function (response) {
                            // console.log("Image,", response)
                            var response = JSON.parse(response)
                            if (response.hasOwnProperty("error")) {
                                console.log(response.error)
                                $("#error_message").html(response.error)
                                $("#error_message").show()
                                $("#loader_img").hide()

                                $("#scan_again").show()
                                $("#timer_sec").html("Scan again in 05 seconds").show()
                                // clearInterval(timerId);
                                timerId.forEach((inter => {
                                    clearInterval(inter)
                                }));
                                if (self.use_timer) {
                                    self.reScan()
                                }


                            }
                            else {
                                // console.log(response.name, response.barcode)
                                var emp_barcode = response.barcode
                                self._onBarcodeScanned(emp_barcode, $("#photo").attr("src"))
                                $("#error_message").hide()
                                $("#scan_again").hide()
                                $("#loader_img").show()

                                $("#timer_sec").html("Scan again in 05 seconds").hide()
                                $("#face_scan_popup").modal('hide')
                                // clearInterval(timerId);
                                timerId.forEach((inter => {
                                    clearInterval(inter)
                                }));

                                interval.forEach((inter => {
                                    clearInterval(inter)
                                }));
                                try {
                                    var mediaStream = video.srcObject;
                                    //                                        console.log("mediaStream", mediaStream)
                                    var tracks = mediaStream.getTracks();
                                    tracks.forEach(track => track.stop())

                                }
                                catch (err) {
                                    console.error(err)
                                }
                            }
                            // var mediaStream = video.srcObject;
                            // console.log("mediaStream", mediaStream)
                            // var tracks = mediaStream.getTracks();
                            // tracks.forEach(track => track.stop())

                            // video.pause();
                            // video.removeAttribute('src'); // empty source
                            // video.load();

                        }
                    });
                }
            } else {
                clearphoto();
            }
        }


        video.addEventListener('loadeddata', () => {
            const displaySize = { width: video.width, height: video.height }
            interval.push(setInterval(async () => {
                const detections = await faceapi.detectAllFaces(video, new faceapi.TinyFaceDetectorOptions()).withFaceLandmarks().withFaceExpressions()
                const resizedDetections = faceapi.resizeResults(detections, displaySize)
                canvas.getContext('2d').clearRect(0, 0, canvas.width, canvas.height)
                faceapi.draw.drawDetections(canvas, resizedDetections)
                faceapi.draw.drawFaceLandmarks(canvas, resizedDetections)
                faceapi.draw.drawFaceExpressions(canvas, resizedDetections)

                if (detections.length >= 1) {
                    var score = detections[0].detection.score
                    if (score > 0.9) {
                        // clearInterval(inter)
                        // clearInterval(timerId);
                        if ($("#photo").attr("src") == "#") {
                            takepicture()
                            // canvas.getContext('2d').clearRect(0, 0, canvas.width, canvas.height)
                            //                                console.log("Teken>>>>>>")
                        }
                        //                            return
                    }
                }
                // if (detections.length > 1) {
                //     alert("Accept one person at a time")
                // }
            }, 100));
        });
    },

    async _onBarcodeScanned(barcode, img) {
        var self = attandance_app;
        const result = await this.rpc('attendance_barcode_scanned',
            {
                'barcode': barcode,
                'token': this.props.token,
                'img': img
            })
        if (result && result.employee_name) {
            this.employeeData = result
            this.switchDisplay('greet')
        }
        else {
            this.displayNotification(_t("No employee corresponding to Badge ID '%(barcode)s.'", { barcode }))
        }
    },


    _stopVideo() {
        // clearInterval(timerId);
        timerId.forEach((inter => {
            clearInterval(inter)
        }));
        interval.forEach((inter => {
            clearInterval(inter)
        }));
        $("#face_scan_popup").modal('hide')
        $("#video_box").show()
        $("#error_message").hide()
        try {
            var mediaStream = video.srcObject;
            //                console.log("mediaStream", mediaStream)
            var tracks = mediaStream.getTracks();
            tracks.forEach(track => track.stop())
        }
        catch (err) {
            console.error(err)
        }
    }
})
