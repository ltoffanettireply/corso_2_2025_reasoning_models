# 🧪 Esercizio con Google AI Studio

## 🔐 Accesso a Google AI Studio

1. Cercare **Google AI Studio** su un browser e cliccare sul primo link disponibile, oppure visitare direttamente [https://aistudio.google.com](https://aistudio.google.com).
2. Se è già impostato un account Google sul PC, l’accesso avverrà automaticamente.
3. In caso contrario:
   - Cliccare su **Sign in to Google AI Studio** nella home page.
   - Effettuare il login con un account Google (è sufficiente un account personale con dominio `@gmail.com`).
4. Una volta effettuato l’accesso, selezionare in alto a sinistra la voce **Chat** (se non si è già nella sezione).
5. Nella barra laterale destra, cliccare su **Run settings**.
6. Per ogni esercizio proposto:
   - provare inizialmente con il modello `Gemini 1.5 Flash` (modello non di reasoning);
   - successivamente, provare con `Gemini 2.5 Pro Preview 05-06` (ultimo modello di reasoning);
   - lasciare invariati gli altri settaggi.

## ✅ Esercizi

Incollare ed eseguire i seguenti prompt nella chat di Google AI Studio ed eseguire le interrogazioni come descritto sopra.

### Prompt 1

```text
Let B be the set of all rectangular boxes with surface area equal to 54 and volume equal to 23. Let r be the radius of the smallest sphere that can contain each box in the set B. The value of r squared can be expressed as a fraction p/q, where p and q are positive integers with no common factors (i.e., relatively prime). What is the value of p + q?
```

**Soluzione attesa**: `721`

---

### Prompt 2

```text
You are an expert algorithm assistant. You will be given a problem description, and your task is to output only the body of the Python function `solve`, with the signature exactly as specified. Do not include any comments, explanations, or blank lines before or after the function. Use 4-space indentation for the function body.

Problem:
You are given an integer array a of size n.

You can perform the following operations any number of times (possibly, zero):

- pay one coin and increase any element of the array by 1 (you must have at least 1 coin to perform this operation);
- gain one coin and decrease any element of the array by 1.

Let's say that an array is 'ideal' if both of the following conditions hold:

- each element of the array is at least 2;
- for each pair of indices i and j (1 <= i, j <= n; i != j) the greatest common divisor (GCD) of a_i and a_j is equal to 1. 
  If the array has less than 2 elements, this condition is automatically satisfied.

Let's say that an array is 'beautiful' if it can be transformed into an 'ideal' array using the aforementioned operations, 
provided that you initially have no coins. If the array is already 'ideal', then it is also 'beautiful'.

The given array is not necessarily 'beautiful' or 'ideal'. You can remove any elements from it 
(including removing the entire array or not removing anything at all). 
Your task is to calculate the minimum number of elements you have to remove (possibly, zero) from 
the array a to make it 'beautiful'.

Write a function called `solve` that accepts two arguments:
- `n`: An integer representing the number n.
- `N_list`: A list of n integers a_1, a_2, ... a_n (a_i >= 2 for each i).

The function should return a single integer representing the minimum number of elements you have to remove 
(possibly, zero) from the array a to make it beautiful.
```

Incollare il testo della funzione generata nel file `test_gemini.py` ed eseguire lo script.  
Lo script testa la funzione scritta su 5 casi di test noti e restituisce il numero di risposte corrette insieme agli eventuali errori.
