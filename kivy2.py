from kivy.app import App
from kivy.lang import Builder
from kivy.uix.boxlayout import BoxLayout
import time
import cv2
import numpy as np
import mapper


Builder.load_string('''
<CameraClick>:
    orientation: 'vertical'
    Camera:
        id: camera
        resolution: (640, 480)
        play: False
    ToggleButton:
        text: 'Play'
        on_press: camera.play = not camera.play
        size_hint_y: None
        height: '48dp'
    Button:
        text: 'Capture'
        size_hint_y: None
        height: '48dp'
        on_press: root.capture()
''')


class CameraClick(BoxLayout):
    def capture(self):
        '''
        Function to capture the images and give them the names
        according to their captured time and date.
        '''
        camera = self.ids['camera']
        timestr = time.strftime("%Y%m%d_%H%M%S")
        camera.export_to_png("Doc{}.png".format(timestr))
        print("Captured")
        image = cv2.imread("Doc{}.png".format(timestr))  # read in the image
        image = cv2.resize(image, (1300, 800))  # resizing because opencv does not work well with bigger images
        orig = image.copy()
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)  # RGB To Gray Scale
        cv2.imshow("Title", gray)

        blurred = cv2.GaussianBlur(gray, (5, 5),
                                   0)  # (5,5) is the kernel size and 0 is sigma that determines the amount of blur
        cv2.imshow("Blur", blurred)

        edged = cv2.Canny(blurred, 30, 50)  # 30 MinThreshold and 50 is the MaxThreshold
        cv2.imshow("Canny", edged)

        contours, hierarchy = cv2.findContours(edged, cv2.RETR_LIST,
                                               cv2.CHAIN_APPROX_SIMPLE)  # retrieve the contours as a list, with simple apprximation model
        contours = sorted(contours, key=cv2.contourArea, reverse=True)

        # the loop extracts the boundary contours of the page
        for c in contours:
            p = cv2.arcLength(c, True)
            approx = cv2.approxPolyDP(c, 0.02 * p, True)

            if len(approx) == 4:
                target = approx
                break
        approx = mapper.mapp(target)  # find endpoints of the sheet

        pts = np.float32([[0, 0], [800, 0], [800, 800], [0, 800]])  # map to 800*800 target window

        op = cv2.getPerspectiveTransform(approx, pts)  # get the top or bird eye view effect
        dst = cv2.warpPerspective(orig, op, (800, 800))

        cv2.imshow("Scanned", dst)

        cv2.waitKey(0)

        cv2.destroyAllWindows()



class TestCamera(App):

    def build(self):
        return CameraClick()


TestCamera().run()


