class AdReqInterface(object):
    def load_picture(self):
        raise Exception("this method should be override by subclass")

    def load_video(self):
        raise Exception("this method should be override by subclass")

    def obtain_picture(self):
        raise Exception("this method should be override by subclass")

    def obtain_video(self):
        raise Exception("this method should be override by subclass")