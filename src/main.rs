use std::{
    io::{prelude::*, BufReader},
    net::{TcpListener, TcpStream},
};
use serde_json::{Result, Value};

mod game;

fn main() {
	let listener = TcpListener::bind("127.0.0.1:13337").unwrap();

    for stream in listener.incoming() {
        let stream = stream.unwrap();

        handle_connection(stream);
    }
}

fn handle_connection(mut stream: TcpStream) {
    let buf_reader = BufReader::new(&stream);
    let http_request: Vec<_> = buf_reader
        .lines()
        .map(|result| result.unwrap())
        .take_while(|line| !line.is_empty())
        .collect();
    println!("Request: {http_request:#?}");
    stream.write_all("HTTP/1.1 200 OK\r\nOK\r\n".as_bytes()).unwrap();
}
