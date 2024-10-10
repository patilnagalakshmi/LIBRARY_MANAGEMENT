import http from 'k6/http';
import { check, sleep } from 'k6';

const BASE_URL = 'http://127.0.0.1:8000';  // Replace with your FastAPI URL

export let options = {
    vus: 5, 
    duration: '30s', 
};

export default function () {
    // Create a unique book ID for testing
    const id = Math.floor(Math.random() * 500)+1;  // Generate a random ID

    // Create a book
    const book = JSON.stringify({
        id: id,
        title: `Test Book ${id}`,
        author: `Test Author ${id}`,
        publication_year: 2024,
        status: "AV",
        category: "Fiction",
        rating: 8
    });

    let res = http.post(`${BASE_URL}/books/`, book, {
        headers: { 'Content-Type': 'application/json' },
    });

    check(res, {
        'book created': (r) => r.status === 200,
    });

    // Get all books
    res = http.get(`${BASE_URL}/books/all`);
    check(res, {
        'retrieved all books': (r) => r.status === 200,
    });

    // Get the newly created book by ID
    res = http.get(`${BASE_URL}/books/${id}`);
    check(res, {
        'retrieved book by ID': (r) => r.status === 200 || r.status === 404,
    });

    // Update the book
    const updatedBook = JSON.stringify({
        id:id,
        title: `Updated Test Book ${id}`,
        author: `Updated Test Author ${id}`,
        publication_year: 2025,
        status: "AV",
        category: "Fiction",
        rating: 9
    });

    res = http.put(`${BASE_URL}/books/${id}`, updatedBook, {
        headers: { 'Content-Type': 'application/json' },
    });
    check(res, {
        'book updated': (r) => r.status === 200,
    });
    // Get all ids 
    let getids = http.get(`${BASE_URL}/books/ids`);
     check(getids, {
         'Get all book ids': (r) => r.status === 200,
     });

     //Get all book names
     let getbooks = http.get(`${BASE_URL}/books/books`);
     check(getbooks, {
         'Get all book names': (r) => r.status === 200,
     });
     

     // Get available books
     let getAvailableBooksRes = http.get(`${BASE_URL}/books/available`);
     check(getAvailableBooksRes, {
         'Get available books': (r) => r.status === 200,
     });
 
     // Get recent books
     let getRecentBooksRes = http.get(`${BASE_URL}/books/recent`);
     check(getRecentBooksRes, {
         'Get recent books': (r) => r.status === 200,
     });
     //get recommadations
     let favo=http.get(`${BASE_URL}/favo`);
     check(favo,{
        'Get Recommadations':(r) =>r.status===200,
     });

    // Delete the book
    let deleteResponse = http.del(`${BASE_URL}/books/${id}`);
    check(deleteResponse, {
        'book deleted': (r) => r.status === 200,
    });
    sleep(1); 
}
