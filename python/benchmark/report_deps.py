import os
import sys

try:
    import torch
    cudnn_version = torch.backends.cudnn.version()
except ImportError:
    cudnn_version = "0.0.0"

def get_cuda_version():
    try:
        cuda_version = os.popen("nvcc --version | grep \"release\" | awk '{print $6}'").read()
        cuda_version = cuda_version[1:-1]
        if not cuda_version:  # 如果cuda_version为空字符串
            cuda_version = 'None'
    except:
        cuda_version = 'None'
    
    return cuda_version

def get_openmpi_version():
    try:
        openmpi_version = os.popen("mpirun --version | grep \"Open MPI\" | awk '{print $4}'").read()
        openmpi_version = openmpi_version[:-1]    
        if not openmpi_version:
            openmpi_version = 'None'
    except:
        openmpi_version = 'None'
    return openmpi_version

def get_gcc_version():
    try:
        gcc_version = os.popen("gcc --version | grep \"GCC\" | awk '{print $3}'").read()
        gcc_version = gcc_version[:-1]
        if not gcc_version:
            gcc_version = 'None'
    except:
        gcc_version = 'None'    
    return gcc_version

def get_nccl_version():
    try:
        nccl_version = os.getenv('NCCL_ROOT')
        pos = nccl_version.find('-')
        nccl_version = nccl_version[pos + 1 : pos + 6]
        if not nccl_version:
            nccl_version = 'None'
    except:
        nccl_version = 'None'    
    return nccl_version

def get_python_version():
    return sys.version[:6]

def check_env_dependence():
    cuda_version = get_cuda_version()
    nccl_version = get_nccl_version()
    openmpi_version = get_openmpi_version()
    python_version = get_python_version()
    gcc_version = get_gcc_version()
    print(f'cuda_version:{cuda_version}, gcc_version:{gcc_version}, cudnn_version:{cudnn_version}, openmpi_version:{openmpi_version}, python_version:{python_version}, nccl_version:{nccl_version}')

def update_markdown_table(md_file, env, table_name, cuda_version, nccl_version, openmpi_version, python_version,  gcc_version):
    markdown_file = md_file  # 替换为实际的Markdown文件路径
    with open(markdown_file, "r") as f:
        lines = f.readlines()
    new_lines = []
    in_table = False

    for line in lines:
        line = line.strip()
        if line.startswith("| " + table_name + " |"):
            new_line = line + env + "|"
            new_lines.append(new_line)
            in_table = True
        elif in_table and line.startswith("|----"):
            new_line = line + "----|"
            new_lines.append(new_line)
        elif in_table and line.startswith("| CUDA_VERSION |"):
            new_line = line + str(cuda_version) + '|'
            new_lines.append(new_line)
        elif in_table and line.startswith("| CUDNN_VERSION |"):
            new_line = line + str(cudnn_version) + '|'
            new_lines.append(new_line)
        elif in_table and line.startswith("| NCCL_VERSION |"):
            new_line = line + str(nccl_version) + '|'
            new_lines.append(new_line)
        elif in_table and line.startswith("| OPENMPI_VERSION |"):
            new_line = line + str(openmpi_version) + '|'
            new_lines.append(new_line)
        elif in_table and line.startswith("| PYTHON_VERSION |"):
            new_line = line + str(python_version) + '|'
            new_lines.append(new_line)
        elif in_table and line.startswith("| GCC_VERSION |"):
            new_line = line + str(gcc_version) + '|'
            new_lines.append(new_line)
        else:
            new_lines.append(line)

    with open(markdown_file, "w") as f:
        f.write("\n".join(new_lines))

if __name__ == "__main__":
    md_file = sys.argv[1]
    env = sys.argv[2]
    table_name = "DEP_VERSION"
    cuda_version = get_cuda_version()
    nccl_version = get_nccl_version()
    openmpi_version = get_openmpi_version()
    python_version = get_python_version()
    gcc_version = get_gcc_version()
    print(f'cuda_version:{cuda_version}, gcc_version:{gcc_version}, cudnn_version:{cudnn_version}, openmpi_version:{openmpi_version}, python_version:{python_version}, nccl_version:{nccl_version}')
    update_markdown_table(md_file, env, table_name, cuda_version, nccl_version, openmpi_version, python_version,  gcc_version)

