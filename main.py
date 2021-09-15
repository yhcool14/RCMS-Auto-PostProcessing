import utils
import os
import argparse
import cv2 as cv
import pysrt
import sys
import re
from xml.etree.ElementTree import Element, SubElement, ElementTree

parser = argparse.ArgumentParser()

parser.add_argument('--vid_path', default='./데이터셋/드론촬영_210525군산/편집/DJI_0001_Trim.MP4', help='raw data vid path: format-.mp4')
parser.add_argument('--srt_path', default='./데이터셋/드론촬영_210525군산/DJI_0001.SRT', help='raw data srt path: format-.SRT')
parser.add_argument('--dozen', default=True, help='Decide to select multi file or not')
# parser.add_argument('--dozen_path', default=None, help='Multi file folder path')
parser.add_argument('--root_path', default='./데이터셋/드론촬영_210525군산/', help='root_path for dozen_path')
parser.add_argument('--frame', type=int, default=30, help='frequency frame for sampling')
parser.add_argument('--save_path', default='./result', help='save path for png and xml')
parser.add_argument('--resize', type=bool, default=True)
parser.add_argument('--folder_name', type=str, default=None, help='save folder_name')
parser.add_argument('--start', type=int, default=None, help='check start frame NUM')
parser.add_argument('--end', type=int, default=None, help='check end frame NUM')

opt = parser.parse_args()
print(opt)

class extract():
    def __init__(self, vid_path, srt_path, frame, save_path, resize, vid_name):
        super(extract, self).__init__()

        self.vid_path   = vid_path
        self.srt_path   = srt_path
        self.vid_name   = vid_name
        self.frame      = frame
        self.frame_list = []
        self.xml_list   = []
        self.txt_list   = []
        self.save_path  = save_path
        self.resize     = resize
        self.ref_list   = ['frame', 'time', 'SrtCnt', 'DiffTime', 'RealTime', 'iso', 'shutter', 'fnum'
                           'ev', 'ct', 'color_md', 'focal_len', 'dzoom_ratio', 'delta', 'latitude', 'longitude',
                           'altitude']
        self.ref_list_perframe = [] # srt_mining할 때마다 refresh 해줘야함
        self.width      = 1920
        self.height     = 1080
        self.depth      = 3
        self.framenum   = None
        self.folder_name= opt.folder_name
        self.clear_index= 0

    def opening(self):
        print("%s opening start!" % self.vid_name)
        if os.path.isfile(self.vid_path):
            self.vidcap = cv.VideoCapture(self.vid_path)
        else:
            print("No file in path_vid")

        if os.path.isfile(self.srt_path):
            self.srt = pysrt.open(self.srt_path)
        else:
            print("No file in path_srt")

    def sampling(self):
        print("%s sampling start!" % self.vid_name)
        # frame_count = 0
        self.opening()
        while(self.vidcap.isOpened()):
            ret, image = self.vidcap.read()

            if(int(self.vidcap.get(1)) % self.frame == 0):
                # print('Saved frame number: ' + str(int(self.vidcap.get(1))))
                # cv.imwrite()
                if self.resize == True:
                    image = cv.resize(image, (1920, 1080))
                self.frame_list.append(image)
                # srt_mining 추가
                self.ref_list_perframe.clear()
                self.srt_mining(index=int(self.vidcap.get(1)) - 1)
                # self.ref_list_perframe list 0번 1번 추가 (1: frame, 2: time)
                ref_list_temp = self.ref_list[0]
                subs_list_temp = self.srt[int(self.vidcap.get(1)) - 1].index
                list_temp = [ref_list_temp, subs_list_temp]
                self.ref_list_perframe.insert(0, list_temp)
                ###
                ref_list_temp = self.ref_list[1]
                subs_list_temp = [self.srt[int(self.vidcap.get(1)) - 1].start, self.srt[int(self.vidcap.get(1)) - 1].end]
                list_temp = [ref_list_temp, subs_list_temp]
                self.ref_list_perframe.insert(1, list_temp)
                ###
                self.xml_make()
                self.txt_list.append(self.ref_list_perframe)
            if ret == False:
                break
        self.vidcap.release()

    def srt_mining(self, index):
        print("%s %d srt_mining start!" %(self.vid_name, self.clear_index))
        subs = self.srt[index]
        subs_list = subs.text_without_tags.splitlines()
        subs_line1 = subs_list[0] # SrtCnt, DiffTime
        subs_line2 = subs_list[1] # YYYY-MM-DD HH:MM:SS,MSS,NSS
        subs_line3 = subs_list[2] # iso, shutter, fnum, ev, ct, color_md, focal_len, dzoom_ratio, latitude, longitude, altitude

        subs_line1_list = subs_line1.replace(',',' ').replace(':',' ').split()
        subs_line2_list = [subs_line2]
        subs_line3_list = subs_line3.replace(',',' ').replace('[',' ').replace(']',' ').split()

        for i in range(len(self.ref_list)-2): # frame, time 제외
            if i < 2:
                ref_list_temp = self.ref_list[i+2]
                subs_list_temp = subs_line1_list[2*i+1]
                list_temp = [ref_list_temp, subs_list_temp]
                self.ref_list_perframe.append(list_temp)
            elif i == 2:
                ref_list_temp = self.ref_list[i + 2]
                # subs_list_temp = subs_line2_list[2 * (i - 2) + 1]
                subs_list_temp = subs_line2_list[0]
                list_temp = [ref_list_temp, subs_list_temp]
                self.ref_list_perframe.append(list_temp)
            elif i > 2:
                ref_list_temp = self.ref_list[i + 2]
                subs_list_temp = subs_line3_list[2 * (i - 3) + 1]
                list_temp = [ref_list_temp, subs_list_temp]
                self.ref_list_perframe.append(list_temp)


    def xml_make(self):
        print("%s %d xml_make start!" % (self.vid_name, self.clear_index))
        self.clear_index = self.clear_index + 1
        # START
        root = Element('annotation')
        # SubElement(root, 'folder').text = self.folder_name
        SubElement(root, 'folder').text = None
        SubElement(root, 'filename').text = self.vid_name + str(self.framenum) + '.png'
        source = SubElement(root, 'source')
        SubElement(source, 'database').text = None # TBU
        SubElement(source, 'annotation').text = None # TBU
        SubElement(source, 'image').text = None # TBU
        SubElement(source, 'flickrid').text = None # TBU
        owner = SubElement(root, 'owner')
        SubElement(owner, 'flickrid').text = None # TBU
        SubElement(owner, 'name').text = None # TBU
        size = SubElement(root, 'size')
        SubElement(size, 'width').text = str(self.width)
        SubElement(size, 'height').text = str(self.height)
        SubElement(size, 'depth').text = str(self.depth)
        dref = SubElement(root, 'dref') # Drone References
        for l in range(len(self.ref_list_perframe)):
            self.ref_list_perframe[l][0] = str(self.ref_list_perframe[l][0])
            self.ref_list_perframe[l][1] = str(self.ref_list_perframe[l][1])
        # self.ref_list_perframe = str(self.ref_list_perframe)
        for i in range(len(self.ref_list)):
            SubElement(dref, self.ref_list_perframe[i][0]).text = self.ref_list_perframe[i][1] # srt_list 작성 후 우변 변경
        object = SubElement(root, 'object')
        SubElement(object, 'name').text = None
        SubElement(object, 'pose').text = None
        SubElement(object, 'truncated').text = None
        SubElement(object, 'difficult').text = None
        bndbox = SubElement(object, 'bndbox')
        SubElement(bndbox, 'xmin').text = None
        SubElement(bndbox, 'ymin').text = None
        SubElement(bndbox, 'xmax').text = None
        SubElement(bndbox, 'ymax').text = None
        # END
        tree = ElementTree(root)
        self.xml_list.append(tree)
        # tree.write('./' + filename + '.xml')

    def saving(self):
        print("%s saving start!" % self.vid_name)
        self.sampling()
        if os.path.exists(self.save_path) == False:
            os.mkdir(self.save_path)
        # Save frame image
        index = 0
        for i in range(len(self.frame_list)):
            cv.imwrite(os.path.join(self.save_path, '%s_frame%d.png' % (self.vid_name, index)), self.frame_list[i])
            index = index + 1
            print("%d frame save done!" % index)
        index = 0
        for i in range(len(self.xml_list)):
            self.xml_list[i].write(os.path.join(self.save_path, '%s_frame%d.xml' % (self.vid_name, index)))
            index = index + 1
            print("%d xml save done!" % index)
        index = 0
        for i in range(len(self.txt_list)):
            f = open(os.path.join(self.save_path, '%s_frame%d.txt' % (self.vid_name, index)), 'w')
            txt_temp = self.txt_list[i]
            for k in range(len(txt_temp)):
                ref = txt_temp[k][0]
                val = txt_temp[k][1]
                data = ref + val + '\n'
                f.write(data)
            f.close()
            index = index + 1
            print("%d txt save done!" % index)
        print("finish!")




def main():
    # subs = pysrt.open('../데이터셋/드론촬영_210525군산/DJI_0001.SRT')
    # temp = subs[0].text_without_tags
    # aa = re.split(': , [ ]', temp)
    # print(aa)
    # print(re.split(': , [ ]', temp))
    if opt.dozen == True:
        file_list = os.listdir(opt.root_path)
        vid_list = [file for file in file_list if file.endswith('.MP4')]
        srt_list = [file for file in file_list if file.endswith('.SRT')]
        try:
            if len(vid_list) != len(srt_list):
                raise Exception('Dont match len_vid and len_srt. Please check the size of file length!') # Require to revise
        except Exception as e:
            sys.exit()
    for multi_index in range(len(vid_list)):
        save_path = os.path.join(opt.save_path, vid_list[multi_index][:-4])
        vid_name = vid_list[multi_index][:-4]
        if os.path.isdir(save_path) == False:
            os.mkdir(save_path)
        extract_temp = extract(vid_path=os.path.join(opt.root_path, vid_list[multi_index]), srt_path=os.path.join(opt.root_path, srt_list[multi_index]),
                               frame=opt.frame, save_path=save_path, resize=opt.resize, vid_name = vid_name)
        extract_temp.saving()
    if opt.dozen == False:
        extract_temp = extract(vid_path=opt.vid_path, srt_path=opt.srt_path, frame=opt.frame, save_path=opt.save_path, resize=opt.resize)
        extract_temp.saving()

if __name__ == '__main__':
    main()