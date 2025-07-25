import shutil
import os

# 원본 파일 경로
source = '/Users/hwangjunho/Desktop/project/boardgame_chatbot/templates/chatbot/logo.png'
# 대상 파일 경로
destination = '/Users/hwangjunho/Desktop/project/boardgame_chatbot/static/chatbot/logo.png'

# 대상 디렉토리가 존재하는지 확인
os.makedirs('/Users/hwangjunho/Desktop/project/boardgame_chatbot/static/chatbot', exist_ok=True)

# 파일 복사
shutil.copy2(source, destination)
print(f"파일이 성공적으로 복사되었습니다: {source} -> {destination}")
