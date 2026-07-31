from fastapi import APIRouter, Depends, status, HTTPException,BackgroundTasks
from sqlalchemy.orm import Session
from app.crud import crud_comment, crud_post,crud_notification
from typing import List

from app.api.dependencies import get_db, get_current_user
from app.models.user import User
from app.schemas.comment import CommentCreate, CommentResponse, CommentUpdate
from app.websockets.manager import manager



router = APIRouter()


# Yorum yapma
@router.post("/post/{post_id}", response_model=CommentResponse, status_code=status.HTTP_201_CREATED)
def create_comment(
        post_id: str,  # Hangi makaleye yorum yapıldığını URL'den alıyoruz
        comment_in: CommentCreate,
        background_tasks: BackgroundTasks,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)  # Yorum yapan kişi tokendan geliyor
):
    """
    Belirli bir makaleye yeni bir yorum ekler.
    Giriş yapmış (token sahibi) kullanıcılar kullanabilir.
    """
    # Önce veritabanına bak, böyle bir makale gerçekten var mı diye
    #crud_post modülünü kullandık!
    post = crud_post.get_post_by_id(db, post_id=post_id)
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Yorum yapılmak istenen makale bulunamadı.")

    # Yorum nesnesini oluştur ve tüm bağlantıları (ilişkileri) kur
    new_comment = crud_comment.create_comment(db=db, comment_in=comment_in, post_id=post_id, author_id=current_user.id)

    #yorum yapan kişi makale sahibi değilse bildirim gönder
    if post.author_id != current_user.id:
        msg_text="Makalene yeni bir yorum yapıldı!"

        #önce db ye kalıcı olarak kaydet
        crud_notification.create_notification(db=db,user_id=post.author_id,message=msg_text)

        #sonra canlı(ws) bildirimini yolla
        notification = {
            "type": "new_comment",
            "post_id": post_id,
            "message": "Makalene yeni bir yorum yapıldı!"
        }
        # İşlemi arka plana atıyoruz (manager.send_personal_message fonksiyonunu hedef kullanıcı ID'si ile çağırır)
        background_tasks.add_task(manager.send_personal_message, notification, post.author_id)

    return new_comment


# Makale yorumlarını listeleme
@router.get("/post/{post_id}", response_model=List[CommentResponse])
def get_comments_for_posts(post_id: str, db: Session = Depends(get_db)):
    """
        Belirli bir makaleye yapılmış tüm yorumları getirir.
        Okumak herkese açıktır (Token gerekmez).
        """
    post = crud_post.get_post_by_id(db, post_id=post_id)
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Makale bulunamadı")

    comments = crud_comment.get_comments_by_post(db=db, post_id=post_id)
    return comments


# yorum güncelle
@router.put("/{comment_id}", response_model=CommentResponse)
def update_comment(
        comment_id: str,
        comment_in: CommentUpdate,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    """
        Bir yorumu günceller.
        Sadece yorumun asıl sahibi (yazarı) güncelleyebilir.
        """
    comment = crud_comment.get_comment_by_id(db=db, comment_id=comment_id)
    if not comment:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Yorum bulunamadı")

    if comment.author_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Bu yorumu güncelleme yetkiniz yok")

    updated_comment = crud_comment.update_comment(db=db, db_comment=comment, comment_in=comment_in)
    return updated_comment


@router.delete("/{comment_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_comment(
        comment_id: str,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    """
        Bir yorumu kalıcı olarak siler.
        Sadece yorumun asıl sahibi (yazarı) silebilir.
        """
    comment = crud_comment.get_comment_by_id(db=db, comment_id=comment_id)
    if not comment:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Yorum bulunamadi")

    #  Yorumu silmeye çalışan kişi, yorumun asıl sahibi mi
    if comment.author_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Bu yorumu silme yetkiniz yok")

    crud_comment.delete_comment(db=db, db_comment=comment)
    return None