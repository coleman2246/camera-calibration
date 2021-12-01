import argparse

import cv2

if __name__ =="__main__":
    # uses argparse to get which video device to use as well as name of file to save to and optionally the height and width of video to capture and stores them in variables
    
    ap = argparse.ArgumentParser()
    ap.add_argument("-v", "--video", required=True, help="path to the (optional) video file")
    ap.add_argument("-o", "--output", required=True, help="path to the output video file")
    ap.add_argument("-r", "--res", type=int, default=None, nargs=2, help="resolution of output video")
    args = vars(ap.parse_args())
    

    video = args["video"]
    output = args["output"]
    width, height = args["res"]

    cap = cv2.VideoCapture(video)
    
    # Check if camera opened successfully
    if (cap.isOpened() == False): 
        print("Unable to read camera feed")
        exit()

    # Default resolutions of the frame are obtained.The default resolutions are system dependent.
    if width is None or height is None:
        frame_width = int(cap.get(3))
        frame_height = int(cap.get(4))
    else:
        frame_height, frame_width = height, width

    out = cv2.VideoWriter(output,cv2.VideoWriter_fourcc('M','J','P','G'), 10, (frame_width,frame_height))
    
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, frame_width)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, frame_height)

    while(True):
        ret, frame = cap.read()
        if ret == True: 
            
            # Write the frame into the file 'output.avi'
            out.write(frame)

            # Display the resulting frame    
            cv2.imshow('frame',frame)

            # Press Q on keyboard to stop recording
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

        # Break the loop
        else:
            break  

    # When everything done, release the video capture and video write objects
    cap.release()
    out.release()

    # Closes all the frames
    cv2.destroyAllWindows()