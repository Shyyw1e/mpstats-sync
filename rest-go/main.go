package main

import (
	"fmt"
	"log"
	"net/http"
	"os/exec"
)


func runPython(script string) ([]byte, error){
	cmd := exec.Command("python3", script)
	return cmd.CombinedOutput()
}

func mainHandler(w http.ResponseWriter, r *http.Request, script string) {
	log.Printf(">> Старт %s", script)
	out, err := runPython("../" + script)
	if err != nil {
		log.Printf("Ошибка: %v\n%s\n", err, out)
		http.Error(w, fmt.Sprintf("Ошибка: \n%s", out), http.StatusInternalServerError)
		return
	}
	w.WriteHeader(http.StatusOK)
	w.Write(out)
}


func main() {
	http.HandleFunc("/sync/lines", func (w http.ResponseWriter, r *http.Request) {
		if r.Method != http.MethodPost {
			http.Error(w, "Метод не поддерживается", http.StatusMethodNotAllowed)
			return
		}
		mainHandler(w, r, "mpstats-sync/main.py")
	})

	http.HandleFunc("/sync/reels", func (w http.ResponseWriter, r *http.Request) {
		if r.Method != http.MethodPost {
			http.Error(w, "Метод не поддерживается", http.StatusMethodNotAllowed)
			return
		}
		mainHandler(w, r, "mpstats-sync/main_reels.py")
	})

	http.HandleFunc("/health", func (w http.ResponseWriter, r *http.Request) {
		w.Write([]byte("ok)"))
	})

	log.Println("REST API запущен на порту :8080")
	log.Fatal(http.ListenAndServe(":8080", nil))
}