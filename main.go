package main

import (
	"crypto/md5"
	"fmt"
	"io"
	"log"
	"os"
	"path/filepath"

	"github.com/mediocregopher/radix.v2/redis"
)

func printFile(path string, info os.FileInfo, err error) error {
	if err != nil {
		log.Print(err)
		return nil
	}
	fmt.Println(path)
	return nil
}

func md5sum(path string, info os.FileInfo, err error) error {
	conn, err := redis.Dial("tcp", "localhost:6379")
	if err != nil {
		log.Fatal(err)
	}
	defer conn.Close()

	if info.IsDir() {
		return nil
	}

        f, err := os.Open(path)
        if err != nil {
                log.Fatal(err)
        }
        defer f.Close()

        h := md5.New()
        if _, err := io.Copy(h, f); err != nil {
                log.Fatal(err)
        }
	
	digest := fmt.Sprintf("%x", h.Sum(nil))
	resp := conn.Cmd("SET", digest, path)
	if resp.Err != nil {
		log.Fatal(resp.Err)
	}
	
        fmt.Printf("%x %v\n", h.Sum(nil), path)
	return nil
}


func main() {
	log.SetFlags(log.Lshortfile)
	dir := os.Args[1]
	err := filepath.Walk(dir, md5sum)
	if err != nil {
		log.Fatal(err)
	}
}
