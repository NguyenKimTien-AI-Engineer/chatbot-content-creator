# Git

### Login git (đăng nhập lúc mới tải git, sau này không cần nữa)

```bash
git config --global user.name "abc"                   # abc là tên tài khoản git, cần vào github để tạo tài khoản trước
git config --global user.email abc@gmail.com          # email dùng để đăng ký tài khoản trên
```

### Create new repository (tạo dự án mới, trưởng dự án tạo)

````bash
git init
git add .
git commit -m "messenger"
git branch -M main
git remote add origin https://github.com/ilyouu/save-public.git       # <<link repository>>.git
git push -u origin main

# ví dụ
# ```
echo "# unity2d-game-sieu-anh-hung" >> README.md
git init
git add README.md
git commit -m "first commit"
git branch -M main
git remote add origin https://github.com/pvbang/unity2d-game-sieu-anh-hung.git
git push -u origin main
# ```
````

### Clone repository (Lấy repository về máy)

```bash
git clone https://github.com/ilyouu/save-public.git       # <<link repository>>.git
```

### Create new branch (Tạo nhánh mới)

```bash
git checkout -b nhanh1      # nhanh1 là tên nhánh, thường đặt tên của bản thân hoặc tính năng mới, ví dụ feature/cat-class
# or
git branch nhanh1
```

### Kiểm tra nhánh

```bash
git branch
```

### Đi đến nhánh khác

```bash
git checkout nhanh1     # nhanh1 là tên nhánh muốn đến
```

### Gộp nhánh

```bash
git checkout main
git merge nhanh1        # gộp nhanh1 vào nhánh main, tức là lưu thay đổi từ nhanh1 vào main
```

### Xoá nhánh

```bash
git checkout -d nhanh1
```

### Xem vị trí hiện tại và các nhánh khác

```bash
git log --oneline
```

### Cập nhật code từ máy lên github

```bash
git add .
git commit -m "note"       # -m "..." nơi viết ghi chú về điều mình vừa thực hiện, ví dụ: git commit -m "Fix: missing eat function"
git push                   # or: git push origin nhanh1
```

### Cập nhật code từ github về máy

```bash
git pull                   # or: git pull origin main
```

### Phục hồi code từ commit cuối

```bash
git restore .
```

### Phục hồi từ commit bất kỳ

```bash
git checkout 000000 -- .      # 000000 là mã commit, sau -- có thể chọn file muốn phục hồi
```

### Cách gộp các lệnh lại làm 1

```bash
# ví dụ muốn gộp 3 câu lệnh:
# git add .
# git commit -m "..."
# git push

git config --global core.editor "notepad"
git config --global --edit
# dưới [alias] thêm dòng sau
up = "!f() { git add . && git commit -m \"$1\" && git push; }; f"

# [user]
# 	name = pvbang
# 	email = pvbang23092002@gmail.com
# [core]
# 	editor = code --wait
# [alias]
# 	up = "!f() { git add . && git commit -m \"$1\" && git push; }; f"

# sau này nếu muốn push một commit lên git thì chỉ cần
git up "message"
```

### Git LFS (github chỉ cho phép upload file <100mb nên nếu cần up file >100mb thì dùng cái này)

```bash
# document
https://git-lfs.com/

# dùng
git lfs install
git lfs track "*.psd"
git add .gitattributes

# ví dụ config trong .gitattributes
*.psd filter=lfs diff=lfs merge=lfs -text
*.psb filter=lfs diff=lfs merge=lfs -text
*.so filter=lfs diff=lfs merge=lfs -text
*.dll filter=lfs diff=lfs merge=lfs -text
*.dylib filter=lfs diff=lfs merge=lfs -text
*.aar filter=lfs diff=lfs merge=lfs -text
Library/PackageCache/com.unity.burst@1.8.7/.Runtime/hostmac/dsymutil filter=lfs diff=lfs merge=lfs -text
*dsymutil filter=lfs diff=lfs merge=lfs -text
```

### Fix lỗi

```bash
# lỗi push khi file quá lớn (ví dụ ở dưới là 12GB)
# nên chia ra và push nhiều lần
git config --global http.postBuffer 12000000000
git config --global https.postBuffer 12000000000
```

### Login in Linux

```bash
git config --global user.name "pvbang"
git config --global user.email pvbang23092002@gmail.com
git config --list
git remote set-url origin https://<token>@github.com/<repo>
```

### Xóa commit cuối

```sh
git reset --soft HEAD~1
```

### Config nhiều tài khoản gihub

```sh
ssh-keygen -t ed25519 -C "bonengonsg@gmail.com"
    # C:\Users\pvban/.ssh/id_ed25519_mekongai

# Git Bash
eval "$(ssh-agent -s)"
ssh-add ~/.ssh/id_ed25519_mekongai
clip < ~/.ssh/id_ed25519_mekongai.pub

# Thêm SSH Key vào tài khoản GitHub:
    # Đăng nhập vào tài khoản GitHub của bạn.
    # Truy cập vào Settings > SSH and GPG keys.
    # Nhấn vào "New SSH Key", đặt tên cho SSH Key (ví dụ: "pvbang"), sau đó dán SSH Key từ clipboard vào ô "Key".

# Cấu hình file SSH để quản lý nhiều tài khoản
nano ~/.ssh/config

Host github.com-pvbang
    HostName github.com
    User git
    IdentityFile C:\Users\pvban\.ssh\pvbang

Host github.com-mekongai
    HostName github.com
    User git
    IdentityFile ~/.ssh/id_ed25519_mekongai


# Sử dụng các tài khoản GitHub khác nhau
git clone git@github.com-pvbang:pvbang/repository.git
git clone git@github.com-mekongai:mekongai/repository.git
```

---

# Hướng dẫn Tạo Nhánh và Xử Lý Merge trên GitHub bằng Git

## 1. Tạo và Quản lý Nhánh (Branches)

### Tạo nhánh mới từ nhánh `dev`:

```bash
git checkout -b dev origin/dev  # copy nhánh dev từ origin sang device
git checkout dev  # Chuyển sang nhánh dev
git pull origin dev  # Đồng bộ với repository trên GitHub
git checkout -b dev_/pvbang  # Tạo nhánh con từ dev
```

---

## 2. Merge Nhánh vào `main`

### Merge từ nhánh con của `dev` vào `main`:

1. Chuyển sang nhánh `dev` để tích hợp nhánh con:
   ```bash
   git checkout dev
   git merge dev_/pvbang
   ```
2. Đồng bộ `dev` với `main`:
   ```bash
   git checkout main
   git merge dev
   ```

---

## 3. Xử Lý Khi Xảy Ra Xung Đột (Conflict)

1. Xem danh sách file bị conflict:
   ```bash
   git status
   ```
2. Mở file để chỉnh sửa thủ công:
   - Dùng VS Code:
     ```bash
     code .
     ```
   - Git sẽ đánh dấu phần conflict trong file:
     ```text
     <<<<<<< HEAD
     (code từ nhánh main)
     =======
     (code từ nhánh đang merge)
     >>>>>>> feature/new-feature
     ```
     Giữ phần code đúng và xóa phần không cần thiết.
3. Sau khi chỉnh sửa xong:
   ```bash
   git add .  # Thêm tất cả file đã sửa
   git commit -m "Resolve conflict: feature/new-feature"
   git push origin main  # Đẩy lên GitHub
   ```

---

## 4. Đẩy Nhánh Mới Lên GitHub

- Khi tạo nhánh mới, cần đẩy nhánh đó lên GitHub:
  ```bash
  git push origin dev_/pvbang
  ```

---

## 5. Xem Danh Sách Các Nhánh

- Danh sách nhánh cục bộ (local):
  ```bash
  git branch
  ```
- Danh sách nhánh trên GitHub (remote):
  ```bash
  git branch -r
  ```

---

## 6. Xóa Nhánh Sau Khi Hoàn Thành

- Xóa nhánh cục bộ:
  ```bash
  git branch -d dev_/pvbang
  ```
- Xóa nhánh trên GitHub (remote):
  ```bash
  git push origin --delete dev_/pvbang
  ```

---

## 7. Quy Trình Tổng Quan

1. **Tạo nhánh mới từ `main` hoặc `dev`.**
2. **Làm việc trên nhánh mới, commit và push lên GitHub.**
3. **Tạo Pull Request (PR) để review code.**
4. **Merge nhánh vào `main` hoặc `dev`.**
5. **Xử lý conflict nếu có.**
6. **Xóa nhánh sau khi hoàn thành.**
