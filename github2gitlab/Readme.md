# 此脚本实现gitlab仓库与github仓库的对齐

### 前提条件：
```
github仓库状态是Public且有master分支
gitlab_user用户具有创建分支权限
```
### 使用说明：
```
此脚本需要访问github，所以使用时需保证网络通畅。
脚本支持多个仓库对其，只需要配置repository的值和对应的参数值即可
同步后不支持在gitlab对应的master-opensource分支做修改
```
### 参数解释：
```
gitlab_dir //拉取github仓库所存放的地方
gitlab_user //gitlab用户
gitlab_token  //gitlab用户对应的token一般需要重新创建一个
gitlab_branch  //在gitlab上与github对齐的分支
gitlab_url  //gitlab clone的https地址，需要去掉前面的https://
github_url  //拉取github仓库的地址
github_project  //github对应的仓库名
```
