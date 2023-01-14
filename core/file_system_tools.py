from core.encoding_tools import get_file_encoding

def get_file_content(file_full_name):
    encoding=get_file_encoding(file_full_name)
    f=open(file_full_name,'r', encoding=encoding)
    content=f.read()
    f.close()
    return content

