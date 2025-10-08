        // Prompt Function
        // function aoDemo() {
        // a = prompt('Enter First number:')
        // console.log(a)
        // a = Number(a);
        // b = prompt('Enter second number:')
        // console.log(b)
        // b = Number(b);
        // // add
        // console.log(a+b)
        // //Subtraction
        // console.log(a-b)
        // //Divide
        // console.log(a/b)
        // //multiply
        // console.log(a*b)
        // }
        // name = prompt('Enter your name')
        // console.log(name)
        // document.getElementById('TextBox1').value = 123
        // // y = document.getElementById('TextBox2').value

        // //console.log(x,y); 
        // alert('Vishnu')
        // document.write("Jigar Vishnu")
        // let x = 'john'
        // console.log(x)


        // Addition function
        function add(){
            x = document.getElementById('TextBox1').value
            x = Number(x);
            y = document.getElementById('TextBox2').value
            y= Number(y);   
            let sum = x + y;
            document.getElementById('result').value = sum; 
            if(x > y){
                let larger = "x is Larger than y";
            }
            else if(y > x){
                larger = "y is Larger than x";
            }
            else{
                larger = "Both are equal";
            }
            document.getElementById('larger').value = larger;
        }
        