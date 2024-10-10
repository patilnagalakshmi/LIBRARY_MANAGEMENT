import oracledb
import asyncio
from concurrent.futures import ThreadPoolExecutor
from pydantic import BaseModel
from typing import List, Optional, Any
from logger import setup_logger

logger = setup_logger('lib.log')

executor: ThreadPoolExecutor = ThreadPoolExecutor()

# Oracle database connection setup
dsn: str = oracledb.makedsn("localhost", 1521, service_name="XE")
config: dict = {
    'user': 'system',
    'password': 'appa',
    'dsn': dsn,
    'min': 1,
    'max': 5,
    'increment': 1
}

# Pydantic model for book representation

class LIBRARY(BaseModel):
    id: Optional[int]
    title: Optional[str]
    author: Optional[str]
    publication_year: Optional[int]
    status: Optional[str]
    category: Optional[str]
    rating: Optional[int]

class OracleDB:
    def __init__(self) -> None:
        self.pool = oracledb.create_pool(**config)

    async def __aenter__(self) -> oracledb.Cursor:
        self.connection: oracledb.Connection = await asyncio.get_running_loop().run_in_executor(executor, self.pool.acquire)
        self.cursor: oracledb.Cursor = self.connection.cursor()
        logger.info('Connection successful')
        return self.cursor

    async def __aexit__(self, exc_type: Optional[type], exc_val: Optional[BaseException], exc_tb: Optional[Any]) -> None:
        if exc_type:
            await asyncio.get_running_loop().run_in_executor(executor, self.connection.rollback)
        else:
            logger.info('Transaction Successful')
            await asyncio.get_running_loop().run_in_executor(executor, self.connection.commit)
        
        await asyncio.get_running_loop().run_in_executor(executor, self.cursor.close)
        await asyncio.get_running_loop().run_in_executor(executor, self.connection.close)
        logger.info('Connection closed')


async def add_book(book: LIBRARY) -> dict[str, str]:
    sql: str = 'INSERT INTO library (id, title, author, publication_year,status,category,rating) VALUES (:1, :2, :3, :4,:5,:6,:7)'
    values: tuple = (book.id, book.title, book.author, book.publication_year, book.status, book.category, book.rating)

    async with OracleDB() as cursor:
        await asyncio.get_running_loop().run_in_executor(executor, cursor.execute, sql, values)
        logger.info('%s added successfully', book)
        return {"message": "Book added successfully."}

async def display_books() -> List[tuple]:
    async with OracleDB() as cursor:
        await asyncio.get_running_loop().run_in_executor(executor, cursor.execute, 'SELECT * FROM library')
        books: List[tuple] = await asyncio.get_running_loop().run_in_executor(executor, cursor.fetchall)
        return books

async def search_book_by_id(book_id: int) -> Optional[tuple]:
    async with OracleDB() as cursor:
        await asyncio.get_running_loop().run_in_executor(executor, cursor.execute, 'SELECT * FROM library WHERE id = :1', (book_id,))
        book: Optional[tuple] = await asyncio.get_running_loop().run_in_executor(executor, cursor.fetchone)
        return book

async def search_book_by_title(title: str) -> Optional[tuple]:
    async with OracleDB() as cursor:
        await asyncio.get_running_loop().run_in_executor(executor, cursor.execute, 'SELECT * FROM library WHERE title = :1', (title,))
        book: Optional[tuple] = await asyncio.get_running_loop().run_in_executor(executor, cursor.fetchone)
        return book

async def search_book_by_author(author: str) -> List[tuple]:
    async with OracleDB() as cursor:
        await asyncio.get_running_loop().run_in_executor(executor, cursor.execute, 'SELECT * FROM library WHERE author = :1', (author,))
        books: List[tuple] = await asyncio.get_running_loop().run_in_executor(executor, cursor.fetchall)
        return books

async def search_books_by_ids(book_ids: List[int]) -> List[tuple]:
    format_strings: str = ','.join([f':{i + 1}' for i in range(len(book_ids))])
    sql: str = f'SELECT * FROM library WHERE id IN ({format_strings})'

    async with OracleDB() as cursor:
        await asyncio.get_running_loop().run_in_executor(executor, cursor.execute, sql, book_ids)
        books: List[tuple] = await asyncio.get_running_loop().run_in_executor(executor, cursor.fetchall)
        return books

async def update_book_by_id(book_id: int, book: LIBRARY) -> dict[str, str]:
    updates: List[str] = []
    params: List[Any] = []

    if book.title:
        updates.append('title = :{}'.format(len(params) + 1))
        params.append(book.title)
    if book.author:
        updates.append('author = :{}'.format(len(params) + 1))
        params.append(book.author)
    if book.publication_year:
        updates.append('publication_year = :{}'.format(len(params) + 1))
        params.append(book.publication_year)
    if book.status:
        updates.append('status = :{}'.format(len(params) + 1))
        params.append(book.status)
    if book.category:
        updates.append('category = :{}'.format(len(params) + 1))
        params.append(book.category)
    if book.rating:
        updates.append('rating = :{}'.format(len(params) + 1))
        params.append(book.rating)

    if updates:
        sql: str = 'UPDATE books SET {} WHERE id = :{}'.format(', '.join(updates), len(params) + 1)
        params.append(book_id)

        async with OracleDB() as cursor:
            await asyncio.get_running_loop().run_in_executor(executor, cursor.execute, sql, params)
            return {"message": "Book updated successfully."}
    else:
        return {"error": "No updates provided."}

async def delete_book_by_id(book_id: int) -> int:
    async with OracleDB() as cursor:
        await asyncio.get_running_loop().run_in_executor(executor, cursor.execute, 'DELETE FROM library WHERE id = :1', (book_id,))
        return cursor.rowcount

async def get_all_book_ids() -> List[tuple]:
    async with OracleDB() as cursor:
        await asyncio.get_running_loop().run_in_executor(executor, cursor.execute, 'SELECT id FROM library')
        book_ids: List[tuple] = await asyncio.get_running_loop().run_in_executor(executor, cursor.fetchall)
        return book_ids

async def get_all_books() -> List[tuple]:
    async with OracleDB() as cursor:
        await asyncio.get_running_loop().run_in_executor(executor, cursor.execute, 'SELECT title FROM library')
        books: List[tuple] = await asyncio.get_running_loop().run_in_executor(executor, cursor.fetchall)
        return books

async def recommendations() -> List[tuple]:
    async with OracleDB() as cursor:
        await asyncio.get_running_loop().run_in_executor(executor, cursor.execute, 'SELECT title FROM library WHERE rating = (SELECT MAX(rating) FROM library)')
        books: List[tuple] = await asyncio.get_running_loop().run_in_executor(executor, cursor.fetchall)
        return books

async def search_book_by_category(category: str) -> List[tuple]:
    async with OracleDB() as cursor:
        await asyncio.get_running_loop().run_in_executor(executor, cursor.execute, 'SELECT * FROM library WHERE category = :1', (category,))
        books: List[tuple] = await asyncio.get_running_loop().run_in_executor(executor, cursor.fetchall)
        return books

async def books_available() -> List[tuple]:
    async with OracleDB() as cursor:
        await asyncio.get_running_loop().run_in_executor(executor, cursor.execute, 'SELECT * FROM library WHERE status = :1', ('AV',))
        books: List[tuple] = await asyncio.get_running_loop().run_in_executor(executor, cursor.fetchall)
        return books

async def recent_books() -> List[tuple]:
    async with OracleDB() as cursor:
        await asyncio.get_running_loop().run_in_executor(executor, cursor.execute, 'SELECT title FROM library WHERE publication_year = (SELECT MAX(publication_year) FROM library)')
        books: List[tuple] = await asyncio.get_running_loop().run_in_executor(executor, cursor.fetchall)
        return books

async def delete_book_by_name(title: str) -> int:
    async with OracleDB() as cursor:
        await asyncio.get_running_loop().run_in_executor(executor, cursor.execute, 'DELETE FROM library WHERE title = :1', (title,))
        return cursor.rowcount
