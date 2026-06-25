# SM4 Java 加速方案调研报告

> 2026-05-16 | 小马 🚀

---

## 一、SM4 算法概述

SM4 是中国国家密码管理局发布的分组密码标准（GB/T 32907-2016），前身是 SMS4。

| 参数 | 值 |
|------|-----|
| 分组长度 | 128 bit |
| 密钥长度 | 128 bit |
| 轮数 | 32 轮 |
| 结构 | 非平衡 Feistel |
| S-Box | 8bit→8bit，固定查表 |

**关键事实：Intel AES-NI 不支持 SM4。** SM4 没有像 AES 那样的 x86 专用硬件指令。这是 SM4 Java 加速的核心挑战。

---

## 二、加速方案分层

```
┌─────────────────────────────────────────────┐
│           Java 应用层                         │
│  BouncyCastle / KonaCrypto / 自定义           │
├─────────────────────────────────────────────┤
│           JCA / JNI / Panama FFI             │
│  JCA Provider / JNI桥接 / FFM API            │
├─────────────────────────────────────────────┤
│           原生加密库                          │
│  OpenSSL 3.x / GmSSL / BabaSSL               │
├─────────────────────────────────────────────┤
│           硬件加速层                          │
│  ARM SM4指令 / x86 SIMD / GPU / QAT卡        │
└─────────────────────────────────────────────┘
```

---

## 三、硬件加速方案

### 3.1 ARM 架构（最优选择）

**Armv8.2+ Crypto Extension 原生支持 SM4：**

- `SM4E` — 单周期完成4个字的轮变换
- `SM4EKEY` — 单周期扩展4个轮密钥
- 8次 SM4E 执行完成一个完整分组加密

**实测性能（阿里云倚天710）：**

| 实现方式 | SM4-ECB 吞吐 | 相对提升 |
|---------|-------------|---------|
| 纯软件（C语言） | ~50 MB/s | 基准 |
| Neon SIMD | ~800 MB/s | **16x** |
| SM4指令 | ~2000 MB/s | **40x** |

已集成到：OpenSSL 主线、libgcrypt、Linux 内核 crypto API

### 3.2 x86 架构

**无专用 SM4 指令**，可用通用 SIMD 优化：

| 方法 | 说明 | 提升幅度 |
|------|------|---------|
| AVX2 通用SIMD | 并行处理多个分组 | ~4-8x |
| AVX-512 通用SIMD | 更宽的向量寄存器 | ~8-12x |
| T-Table 消除 | 避免缓存时序攻击 | 安全性提升 |

龙蜥白皮书数据：x86 SIMD优化后 SM4 提升最大 **8倍**。

### 3.3 GPU 加速

- **CUDA**: 已有学术论文实现（ACM ICCS 2021），适合大批量离线加密
- 吞吐量可达数十 GB/s（取决于GPU型号）
- **不适合低延迟在线场景**（PCIe传输延迟 > 加密延迟）

### 3.4 Intel QAT 加速卡

- 硬件加速卡（PCIe），支持 SM4
- ⚠️ **QAT-Java SDK 目前仅支持压缩（DEFLATE/LZ4/ZSTD），不支持加密**
- 可通过 OpenSSL QAT Engine 间接使用，但需 C 层中转

---

## 四、Java 生态库对比

### 4.1 核心方案

| 方案 | 类型 | 平台 | 性能 | 推荐度 |
|------|------|------|------|-------|
| **TencentKonaSMSuite (KonaCrypto-Native)** | JNI+OpenSSL | Linux x64/aarch64 | ⭐⭐⭐⭐⭐ | **首选** |
| **Tencent Kona JDK** | 定制JDK | Linux/macOS/Win, x64/aarch64 | ⭐⭐⭐⭐⭐ | 首选（可换JDK场景） |
| BouncyCastle | 纯Java | 全平台 | ⭐⭐ | 通用备选 |
| KonaCrypto（纯Java版） | 纯Java | 全平台 | ⭐⭐⭐ | 无JNI需求时 |
| JNI自研（调GmSSL） | JNI | 需自行编译 | ⭐⭐⭐⭐ | 有定制需求时 |

### 4.2 TencentKonaSMSuite 详解

**版本**: v1.0.19 (Maven Central)
**许可**: GPL v2 with classpath exception
**JDK**: 8/11/17/21/25 LTS
**签名**: Oracle JCE 签名（可在 Oracle JDK 上运行）

```xml
<!-- 纯Java版 -->
<dependency>
    <groupId>com.tencent.kona</groupId>
    <artifactId>kona-crypto</artifactId>
    <version>1.0.19</version>
</dependency>

<!-- JNI加速版（推荐） -->
<dependency>
    <groupId>com.tencent.kona</groupId>
    <artifactId>kona-crypto</artifactId>
    <version>1.0.19</version>
    <classifier>native</classifier>
</dependency>
```

**加速原理**：KonaCrypto-Native 通过 JNI 调用底层 OpenSSL 3.x，OpenSSL 内部自动使用 ARM SM4 指令或 x86 SIMD 优化。Java 层零感知，性能提升完全透明。

**特性**：
- PhantomReference 自动管理 JNI native 内存，无内存泄漏风险
- 支持 SM2/SM3/SM4 全套
- 支持 TLCP / TLS 1.3 RFC 8998

### 4.3 BouncyCastle

最通用的 Java 加密库，SM4 通过 `SM4Engine` 实现。

```java
// 标准 JCA 用法
Cipher cipher = Cipher.getInstance("SM4/ECB/PKCS5Padding", "BC");
```

**缺点**：
- 纯 Java 实现，无法利用硬件指令
- 性能约 50-80 MB/s（单线程），比 KonaCrypto-Native 慢 **5-10倍**
- 无 SM 协议（TLCP/RFC 8998）支持

---

## 五、前沿方向

### 5.1 Java Panama FFI (JDK 22+ 正式)

**替代 JNI 的新一代外部函数接口：**

```java
// 示例：通过 Panama 直接调用 GmSSL
Linker linker = Linker.nativeLinker();
SymbolLookup lookup = SymbolLookup.libraryLookup("libgmssl", MemorySession.openImplicit());
MethodHandle sm4_encrypt = linker.downcallHandle(
    lookup.lookup("sm4_encrypt"), 
    FunctionDescriptor.of(ValueLayout.JAVA_INT, ...)
);
```

**优势**：
- 不需要写 C JNI 胶水代码
- 调用开销比 JNI 低（bounded calls）
- Memory API 安全管理 native 内存

**现状**：JDK 22 正式版，生态尚不成熟，无现成的 SM4 FFI 封装库。

### 5.2 Panama Vector API (JDK 24+ 预览)

直接在 Java 中使用 SIMD 指令操作向量寄存器，理论上可在纯 Java 层实现 AES-NI 级别的优化。但目前仍是预览特性，API 可能变化。

---

## 六、性能预估总结

| 场景 | 方案 | 预估吞吐（单线程） | 备注 |
|------|------|-------------------|------|
| x86 通用 | BouncyCastle | 50-80 MB/s | 纯Java基准 |
| x86 通用 | KonaCrypto-Native | 400-800 MB/s | OpenSSL SIMD |
| ARM 服务器 | KonaCrypto-Native | 1000-2000 MB/s | ARM SM4指令 |
| x86 自研JNI | GmSSL/BabaSSL JNI | 400-800 MB/s | 同OpenSSL SIMD |
| 大批量离线 | GPU CUDA | 10-50 GB/s | 需自行实现 |

---

## 七、选型建议

### 推荐方案（按场景）

**1. 生产环境首选 → TencentKonaSMSuite (KonaCrypto-Native)**
- 理由：Maven 直接用、Oracle JDK 兼容、自动 JNI 内存管理、SSL 协议全覆盖
- 一步到位，性能提升 5-10x
- 零侵入：只需加依赖，代码用标准 JCA API

**2. 可换 JDK 场景 → Tencent Kona JDK 8/11/17/21**
- 理由：JDK 内置国密支持，连依赖都不用加
- Kona JDK 8 和 17 已原生支持 SM2/3/4 + TLCP

**3. 全平台/Android → KonaCrypto（纯Java版）或 BouncyCastle**
- 理由：无 JNI 依赖，ARM/Windows/macOS 通用
- 性能不如 Native 版，但胜在兼容性

**4. 极致性能/定制需求 → JNI 自研（OpenSSL/GmSSL/BabaSSL）**
- 理由：完全控制底层实现
- 代价：需自己维护 JNI 桥接代码

### 实施路径

```
现有项目用 BouncyCastle SM4
    → 换 KonaCrypto-Native（改1行Maven依赖）
    → 标准JCA API不变，自动获得硬件加速
    → 完成
```

**核心结论：SM4 Java 加速的最佳路径不是自己造轮子，而是换底层 Provider。KonaCrypto-Native 把 OpenSSL 的 SIMD/指令集优化透明地暴露给 Java，零代码改动即获得 5-40x 性能提升。**

---

## 参考来源

1. 龙蜥国密白皮书 - https://openanolis.github.io/whitebook-shangmi/optimization.html
2. TencentKonaSMSuite - https://github.com/tencent/TencentKonaSMSuite
3. OpenSSL SM4 ARM汇编 - https://github.com/openssl/openssl/blob/master/crypto/sm4/asm/sm4-armv8.pl
4. RISC-V SM4 ISA扩展 (arXiv:2002.07041)
5. CUDA SM4并行实现 (ACM ICCS 2021)
6. Intel QAT - https://www.intel.com/content/www/us/en/products/docs/accelerator-engines/what-is-intel-qat.html
7. BouncyCastle SM4Engine - https://downloads.bouncycastle.org/java/docs/bcprov-jdk14-javadoc/
8. Java Panama FFI - https://docs.oracle.com/en/java/javase/21/core/foreign-function-and-memory-api.html
9. GmSSL - https://github.com/guanzhi/GmSSL
10. BabaSSL - https://github.com BabaSSL/BabaSSL
