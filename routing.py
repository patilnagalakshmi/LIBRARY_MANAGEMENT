from fastapi import APIRouter, HTTPException
from service import add_book, display_books, search_book_by_id, search_books_by_ids, update_book_by_id, delete_book_by_id, LIBRARY,search_book_by_title,search_book_by_author,get_all_book_ids,get_all_books,recommendations,search_book_by_category,books_available,recent_books,delete_book_by_name
from  logger import setup_logger

router = APIRouter()
logger = setup_logger('lib.log')

@router.get("/")
async def index():
    return {"task":"Welcome to Library Management"}

@router.post("/books/")
async def create_book(book: LIBRARY):
    logger.info('Creating book: %s', book)
    return await add_book(book)

@router.get("/books/all")
async def get_books():
    books = await display_books()
    if not books:
        logger.info('No books found.')
        return {"message": "No books found."}
    logger.info('Books retrieved: %s', books)
    return {"books": books}

@router.get("/books/ids")
async def get_ids():
    book_ids=await get_all_book_ids()
    return book_ids

@router.get("/books/books")
async def get_all_booknames():
    books=await get_all_books()
    return books


@router.get("/books/title/")
async def get_books_by_title(title:str):
    book=await search_book_by_title(title)
    if book:
        logger.info('Books found for title: %s', title)
        return {"id": book[0], "title": book[1], "author": book[2], "publication_year": book[3],"status":book[4],"category":book[5],"rating":book[6]}
    else:
        logger.error('No books found for title: %s', title)
        raise HTTPException(status_code=404, detail="No books found for the given title.")

@router.get("/books/author/")
async def get_books_by_author(author:str):
    books=await search_book_by_author(author)
    if books:
        logger.info('Books found : %s', author)
        return [{"id": book[0], "title": book[1], "author": book[2], "publication_year": book[3],"status":book[4],"category":book[5],"rating":book[6]} for book in books]
    else:
        logger.error('No books found : %s', author)
        raise HTTPException(status_code=404, detail="No books found for the given author.")

@router.get("/books/category/")
async def get_books_by_category(category:str):
    books=await search_book_by_category(category)
    if books:
        logger.info('Books found : %s', category)
        return [{"id": book[0], "title": book[1], "author": book[2], "publication_year": book[3],"status":book[4],"category":book[5],"rating":book[6]} for book in books]
    else:
        logger.error('No books found : %s', category)
        raise HTTPException(status_code=404, detail="No books found for the given category.")

@router.get("/books/available")
async def available():
    books=await books_available()
    if books:
        logger.info('Fetched available books')
        return {"available_books": books}
    else:
        logger.error('No available books found')
        raise HTTPException(status_code=404, detail="No available books found.")

@router.get("/books/recent")
async def recent():
    books=await recent_books()
    return books

@router.get("/books/{book_id}")
async def get_book(book_id: int):
    book = await search_book_by_id(book_id)
    if book:
        logger.info('Book found: %s', book)
        return {"id": book[0], "title": book[1], "author": book[2], "publication_year": book[3],"status":book[4],"category":book[5],"rating":book[6]}
    else:
        logger.warning('Book not found for ID: %d', book_id)
        raise HTTPException(status_code=404, detail="Book not found.")

@router.get("/books/")
async def get_books_by_ids(book_ids: str):
    book_ids_list = [int(id.strip()) for id in book_ids.split(',')]
    books = await search_books_by_ids(book_ids_list)
    if books:
        logger.info('Books found for IDs: %s', book_ids_list)
        return [{"id": book[0], "title": book[1], "author": book[2], "publication_year": book[3],"status":book[4],"category":book[5],"rating":book[6]} for book in books]
    else:
        logger.error('No books found for IDs: %s', book_ids_list)
        raise HTTPException(status_code=404, detail="No books found for the given IDs.")

@router.put("/books/{book_id}")
async def update_book(book_id: int, book:LIBRARY):
    logger.info('Updating book ID: %d with data: %s', book_id, book)
    result = await update_book_by_id(book_id, book)
    if "error" in result:
        logger.error('No book found for ID')
        raise HTTPException(status_code=400, detail=result["error"])
    return result

@router.delete("/books/del/{book_id}")
async def delete_book(book_id: int):
    logger.info('Deleting book with ID: %d', book_id)
    result = await delete_book_by_id(book_id)
    if result == 0:
        logger.warning('Book not found for deletion ID: %d', book_id)
        raise HTTPException(status_code=404, detail="Book not found.")
    return {"message": "Book deleted successfully."}

@router.delete("/delete")
async def delete_by_title(title:str):
    logger.info('Deleting book by name:%s',title)
    result=await delete_book_by_name(title)
    if result==0:
        logger.warning('Book not found')
        raise HTTPException(status_code=404, detail="Book not found.")
    return {"message": "Book deleted successfully."}

@router.get("/favo")
async def favo():
    books=await recommendations()
    return books

