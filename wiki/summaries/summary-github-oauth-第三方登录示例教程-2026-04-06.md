---
title: "摘要 — GitHub OAuth 第三方登录示例教程"
type: summary
status: draft
created: 2026-04-06
updated: 2026-04-06
sources:
  - raw/github-oauth-第三方登录示例教程-2026-04-06.md
links:
  - https://www.ruanyifeng.com/blog/2019/04/github-oauth.html
tags:
  - oauth
  - web-dev
---

# 摘要 — GitHub OAuth 第三方登录示例教程

## 来源元数据

| 字段        | 值                              |
|--------------|----------------------------------|
| 来源类型     | blog |
| 作者         | 阮一峰                          |
| 年份         | 2019                            |
| 发表于       | 阮一峰的网络日志             |
| Raw 文件     | `raw/github-oauth-第三方登录示例教程-2026-04-06.md` |

## 主要观点

OAuth 授权码流程的完整实战演示，以 GitHub 为例展示第三方登录的六个步骤：跳转授权 → 用户同意 → 获取授权码 → 请求令牌 → 获取令牌 → 调用 API。

## 关键细节

- 第三方登录本质是 OAuth 授权：A 网站让用户提供第三方网站的身份证明
- 授权码通过前端传送，令牌储存在后端，前后端分离避免令牌泄漏
- GitHub OAuth 端点：`/login/oauth/authorize`（授权）、`/login/oauth/access_token`（令牌）
- 令牌使用：在 HTTP 头信息加上 `Authorization: token <access_token>`

## 方法 / 进路

使用 Koa 框架实现后端 OAuth 流程：
1. 前端提供跳转链接（带 `client_id` 和 `redirect_uri`）
2. 后端 `/oauth/redirect` 路由接收授权码
3. 后端用授权码 + `client_secret` 向 GitHub 请求令牌
4. 后端用令牌调用 GitHub API 获取用户数据

## 结果 / 证据

完整代码示例仓库：[node-oauth-demo](https://github.com/ruanyf/node-oauth-demo)，演示了从授权到获取用户名的全流程。

## 局限性

- 示例简化了安全考量（生产环境需要更严格的令牌存储和刷新机制）
- 仅演示授权码方式，不涉及其他三种 OAuth 授权类型

## 链接到概念

- [[OAuth-2.0]] — 本文是授权码方式的实战演示
- [[授权码授权]] — 本文演示的具体授权类型

## 链接到主题

- [[OAuth-授权机制]] — OAuth 系列教程的实战部分

## 值得保留的引用

> 所谓第三方登录，实质就是 OAuth 授权。用户想要登录 A 网站，A 网站让用户提供第三方网站的数据，证明自己的身份。