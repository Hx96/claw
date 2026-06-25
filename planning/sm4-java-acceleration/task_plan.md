# SM4 Java 加速调研

## 目标
调研 SM4 国密加密算法在 Java 环境下的加速方案，覆盖：硬件指令集加速、JNI/本地库、纯Java优化、库对比。

## 阶段

### Phase 1: SM4 基础与标准库 [complete]
- SM4 算法特性（分组密码、密钥长度、轮数）
- Java 标准实现（BouncyCastle、JDK 内置支持情况）
- 基准性能数据

### Phase 2: 硬件加速方案 [complete]
- Intel AES-NI/SM4 指令集扩展
- ARM CE 加密扩展
- GPU 加速（OpenCL/CUDA）

### Phase 3: JNI/本地库方案 [complete]
- GmSSL (C库)
- OpenSSL 3.x SM4
- KCP/其他本地库

### Phase 4: Java 生态库对比 [complete]
- BouncyCastle SM4
- 小米 MISecure
- 阿里巴巴 BabaSSL
- 其他开源方案

### Phase 5: 综合对比与建议 [complete]
- 性能对比矩阵
- 选型建议
