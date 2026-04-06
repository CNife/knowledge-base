---
title: OAuth 授权机制
type: topic
status: draft
created: 2026-04-07
updated: 2026-04-07
sources:
  - raw/oauth-2.0-的四种方式-2026-04-06.md
  - raw/oauth-2.0-的四种方式-2026-04-06.md
  - raw/github-oauth-第三方登录示例教程-2026-04-06.md
links:
  - "https://www.ruanyifeng.com/blog/2019/04/oauth_design.html"
  - "https://www.ruanyifeng.com/blog/2019/04/oauth-grant-types.html"
  - "https://www.ruanyifeng.com/blog/2019/04/github-oauth.html"
tags:
  - oauth
  - web-dev
  - authorization
---

# OAuth 授权机制

## 范围

OAuth 授权机制涵盖 OAuth 2.0 协议的核心概念、四种授权方式及其应用场景。属于 Web 开发与 API 安全领域。

本主题解释 OAuth 如何通过令牌（token）机制实现第三方应用对用户数据的有限、可控、可撤销访问，以及不同授权类型的选择策略。不涉及 OAuth 1.0 或 OpenID Connect 等扩展协议。

## 子问题

1. OAuth 的核心设计思想与令牌机制
2. 四种授权类型的适用场景与安全性对比
3. 令牌的刷新与撤销机制
4. 实战：GitHub OAuth 第三方登录实现

## 关键进路

### 进路 1：授权码授权（Authorization Code Grant）

最安全的授权方式，适用于有后端的 Web 应用。授权码通过前端传递，令牌在后端存储，避免令牌泄漏。流程：前端跳转授权端点 → 用户同意返回授权码 → 后端用授权码 + client_secret 请求令牌 → 授权服务器返回令牌。被 GitHub、Google 等主流平台采用。

### 进路 2：隐藏式授权（Implicit Grant）

适用于纯前端应用（如单页应用）。令牌直接在 URL 锚点返回，不经过后端。安全性较低，因为令牌在前端暴露，仅适合低安全要求场景。RFC 6749 规定令牌在 URL 锚点（#）而非查询字符串，减少中间人攻击风险。

### 进路 3：密码式授权（Resource Owner Password Credentials Grant）

用户直接向应用提供用户名和密码，应用用凭证换取令牌。风险最高，仅适用于高度信任的场景（如操作系统自带应用或第一方应用）。不推荐用于第三方应用。

### 进路 4：凭证式授权（Client Credentials Grant）

应用用自己的 client_id 和 client_secret 直接请求令牌，无需用户参与。适用于命令行应用或后端服务之间的认证。令牌针对应用而非用户，多用户可能共享同一令牌。

## 系统 / 论文概览

| 名称 | 年份 | 关键贡献 | 链接 |
|------|------|----------|------|
| RFC 6749 | 2012 | OAuth 2.0 核心规范，定义四种授权类型 | [RFC 6749](https://tools.ietf.org/html/rfc6749) |
| 阮一峰 OAuth 系列 | 2019 | 中文通俗解释与实战示例 | [[summary-oauth-20-的一个简单解释-2026-04-06]] [[summary-oauth-20-的四种方式-2026-04-06]] |
| GitHub OAuth 实战 | 2019 | 授权码方式的完整代码示例 | [[summary-github-oauth-第三方登录示例教程-2026-04-06]] |

## 重要参考

- 阮一峰（2019）— "OAuth 2.0 的一个简单解释" — [[summary-oauth-20-的一个简单解释-2026-04-06]] — 用"快递员进小区"类比解释 OAuth 核心价值
- 阮一峰（2019）— "OAuth 2.0 的四种授权方式" — [[summary-oauth-20-的四种方式-2026-04-06]] — 详解四种授权类型的适用场景与安全性
- 阮一峰（2019）— "GitHub OAuth 第三方登录示例教程" — [[summary-github-oauth-第三方登录示例教程-2026-04-06]] — 授权码方式的完整实战演示
- IETF（2012）— "RFC 6749: The OAuth 2.0 Authorization Framework" — 官方规范

## 待解决问题

- OAuth 2.0 的令牌泄漏风险：令牌泄漏后果等同于密码泄漏，生产环境需要更严格的存储和刷新机制 [未验证]
- 隐藏式授权在现代前端框架中的最佳实践 [未验证]
- OAuth 2.1 对隐藏式授权的废弃趋势 [未验证]

## 相关主题

[[LLM-辅助知识管理]]
