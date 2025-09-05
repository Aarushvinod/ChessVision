import cv2
import numpy as np
from detectron2.config import get_cfg 
from detectron2.engine import DefaultPredictor
from detectron2.projects import point_rend
from BoardRecognizerFullGame import BoardRecognizerFullGame
import torch.cuda as GPU
from pathlib import Path

#Primary class holding all Board Recognition logic
#The fields of the class are the piece detector, the board detector, and the target image
#This is meant to be used as a one-shot detector for images

class ImageBoardRecognizer:

    def __init__(self, pieces_name: str, board_name: str):
        #The class has two fields, the piece detector and the board detector models.
        self.board_recognizer = BoardRecognizerFullGame(pieces_name)
        cfg = get_cfg()
        point_rend.add_pointrend_config(cfg)
        merge_path = Path(__file__).resolve().parents[1] / "detecron2" / "projects/PointRend/configs/InstanceSegmentation/pointrend_rcnn_X_101_32x8d_FPN_3x_coco.yaml"
        cfg.merge_from_file(merge_path)
        cfg.MODEL.DEVICE = "cpu" if not GPU.is_available() else "cuda"
        cfg.MODEL.WEIGHTS = board_name
        cfg.MODEL.ROI_HEADS.SCORE_THRESH_TEST = 0.7
        cfg.MODEL.ROI_HEADS.NUM_CLASSES = 2
        cfg.MODEL.POINT_HEAD.NUM_CLASSES = 2
        self.board_detector = DefaultPredictor(cfg)
    
    #Sets target image after reszing to 1280x128

    def set_image(self, image):
        self.image = cv2.resize(image, (1280, 1280))
        self.board_recognizer.set_image(self.image)
        
    #Runs board detection and generates a polygon contour
    #Slightly more code because the intitial mask is a binary mask and needs to be converted to a polygon

    def run_board_detection(self, **kwargs):
        prediction = self.board_detector(self.image)
        binary_mask = prediction['instances'].get('pred_masks')[0].numpy().astype('uint8') if not GPU.is_available() else  prediction['instances'].get('pred_masks')[0].cpu().numpy().astype('uint8')
        contours, _ = cv2.findContours(binary_mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        copy_image = self.image.copy()
        final_mask = max(contours, key=len)
        if kwargs.get('save'):
            cv2.drawContours(copy_image, [final_mask], 0, (255, 0, 0), 3)
            cv2.imwrite("board_detection.jpg", copy_image)
        return final_mask

    #Applies perspective transformation to source image and generates transformation matrix
    #For now perspective transform is done by taking the 4 most extreme points of the board polygon
    #These points are matched to corresponding corners and perspective transformation is applied

    def perspective_transform(self, board_contour):
        tl, tr, bl, br = None, None, None, None
        for point in board_contour:
            x, y = point[0]
            tl = point[0] if tl is None or (x+y) < (tl[0] + tl[1]) else tl
            br = point[0] if br is None or (x+y) > (br[0] + br[1]) else br
            tr = point[0] if tr is None or (x-y) > (tr[0] - tr[1]) else tr
            bl = point[0] if bl is None or (x-y) < (bl[0] - bl[1]) else bl
        corners = np.float32([tl, tr, bl, br])
        transformed = np.float32([[0, 0], [self.image.shape[1], 0],[0, self.image.shape[0]], [self.image.shape[1], self.image.shape[0]]])
        self.board_recognizer.homography = cv2.getPerspectiveTransform(corners, transformed)
        warped_image = cv2.warpPerspective(self.image, self.board_recognizer.homography, self.image.shape[:2][::-1])
        return warped_image
    
    def run_piece_detection(self, confidence, **kwargs):
        return self.board_recognizer.run_piece_detection(confidence, **kwargs)

    def find_board(self, warped_frame, boxes, classes, **kwargs):
        return self.board_recognizer.find_board(warped_frame, boxes, classes, **kwargs)
    
    def print_board(self, board):
        self.board_recognizer.print_board(board)
    
    def get_rotation(self, board):
        return self.board_recognizer.get_rotation(board)

    def make_pychess_board(self, board, **kwargs):
        return self.board_recognizer.make_pychess_board(board, **kwargs)