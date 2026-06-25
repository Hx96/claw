# SM4 Java 加速 - 调研发现

## 发现记录

### 1. SM4 算法基础
- 分组密码，128bit分组，128bit密钥，32轮Feistel结构
- 无x86专用指令（AES-NI不支持SM4）
- ARMv8.2+ Crypto Extension 原生支持SM4指令（SM4E/SM4EKEY）

### 2. 硬件加速
- **ARM**: Armv8.2 FEAT_SM4，SM4E/SM4EKEY指令，OpenSSL/GmSSL已集成
  - 倚天710实测：SIMD优化后SM4-CTR提升最大40倍
- **x86**: 无原生SM4指令，可用通用SIMD（AVX2/AVX-512）优化
  - 龙蜥白皮书：x86 SIMD优化SM4提升最大8倍
- **RISC-V**: 轻量级ISA扩展（arXiv:2002.07041，6条指令实现SM4 quarter-round）
- **GPU**: CUDA并行SM4实现（ACM论文），适合大批量离线加密
- **Intel QAT**: 硬件加速卡，支持SM4但QAT-Java SDK目前仅支持压缩，不支持加密

### 3. Java生态库
| 库 | 类型 | 特点 | 加速方式 |
|---|---|---|---|
| BouncyCastle | 纯Java | 最通用，JCA Provider，SM4Engine | 无硬件加速 |
| TencentKonaSMSuite (KonaCrypto) | 纯Java | 腾讯出品，JCA Provider，Maven中央仓库 | 纯Java实现 |
| KonaCrypto-Native | JNI+OpenSSL | 同上，但底层调用OpenSSL | **间接获得OpenSSL SIMD优化** |
| Tencent Kona JDK | 定制JDK | 8/11/17/21 LTS，原生国密支持 | 同上 |
| BabaSSL | C库(阿里) | OpenSSL fork，深度SM4优化 | ARM SM4指令+SIMD |
| GmSSL | C库(北大) | 国密专用，SM2/3/4/9 | ARM SM4指令+SIMD |

### 4. KonaCrypto-Native 是关键
- 腾讯出品，v1.0.19，GPL v2 with classpath exception
- 支持 JDK 8/11/17/21/25
- 仅 Linux x86_64/aarch64
- JNI调用OpenSSL底层实现，自动管理native内存（PhantomReference）
- Oracle JCE签名，可在Oracle JDK上运行
- Maven中央仓库直接可用：com.tencent.kona:kona-crypto

### 5. Java Panama FFI (JDK 22+ 正式)
- 替代JNI的新方案，FFM API
- 可直接调用C库（GmSSL/BabaSSL/OpenSSL）而无需写JNI代码
- Panama Vector API（JDK 24+）可直接使用SIMD指令
- 未来潜力大但目前生态不成熟

### 6. 性能数据
- BouncyCastle SM4 (纯Java): 约 50-80 MB/s (单线程)
- OpenSSL SM4 (x86-64, SIMD): 约 400-800 MB/s
- OpenSSL SM4 (aarch64, SM4指令): 约 1000-2000 MB/s
- ARM Neon优化SM4: 比软件实现提升40倍
- x86 SIMD优化SM4: 比软件实现提升8倍
- KonaCrypto-Native ≈ OpenSSL性能（JNI调用开销可忽略）
