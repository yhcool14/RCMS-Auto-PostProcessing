# RCMS-Postprocessing-for-video

본 프로그램은 .MP4(영상)과 .SRT(드론래퍼런스)를 입력으로 받아서 사용자 지정 프레임 단위로 PNG, XML, TXT 세 가지의 파일을 생성하는 코드입니다.

To Do List
1. TXT와 XML 특정 요소 수정
2. 저장 경로를 지정해줄때, 상대 경로로 PNG가 저장이되지 않는 오류 수정
3. Print로 진행상황알려줄때, 단지 현재 진행 Frame만 나오게 하지말고 [Frame/total_frame]으로 진행상황을 파악할 수 있도록 변경
4. .MP4와 .SRT를 입력으로 받았을 때, 현재는 모든 영상에 대해서 파일을 생성하는데, 특정 구간만 출력할 수 있는 기능 추가

Dataset

처리하고자 하는 데이터셋을 main.py와 같은 폴더 내에 따로 데이터셋 폴더를 생성하여 넣으세요. 동일 폴더 내에 데이터셋 폴더가 없으면 파일이 생성되지 않는 오류가 발생합니다.

How to Use?
1) 영상이 하나일 경우
    python main.py --vid_path @.MP4경로 --srt_path @.SRT경로 --dozen False --frame @처리프레임단위 --save_path @PNG,XML,TXT저장경로_Result폴더만필요(추천)
2) 영상이 여러개일 경우
    python main.py  --dozen True --root_path @.MP4와.SRT가들어있는경로 --frame @처리프레임단위
