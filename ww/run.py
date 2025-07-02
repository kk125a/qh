import os
import sys
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent
sys.path.append(str(project_root))

# 运行Streamlit应用
if __name__ == "__main__":
    os.system(f"streamlit run {project_root}/app/main.py") 