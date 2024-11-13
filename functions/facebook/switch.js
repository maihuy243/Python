const fs = require('fs');
const path = require('path');
const filePath = path.join(__dirname, 'via.txt');

fs.readFile(filePath, 'utf8', (err, data) => {
    if (err) {
        console.error('Lỗi khi đọc file:', err);
        return;
    }
    const dataChange = data.split('\n').filter(e => e).map((e) => {
        const acc = e.replace("\r", "")
        const [user, twoFa, pass, ...end] = acc?.split('|')
        const newData = twoFa.length === 32 ? [user, pass, twoFa, ...end].join('|') : acc
        return newData
    })

    const convertToString = dataChange.join('\n')

    // Replace file
    fs.writeFile(filePath, convertToString, 'utf8', (err) => {
        if (err) {
            console.error('Lỗi khi ghi file:', err);
            return;
        }
        console.log('Nội dung file đã được thay đổi!');
    });
});

