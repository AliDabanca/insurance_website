const customers = [
    {
        first_name: "Ali",
        last_name: "Yılmaz",
        tc_id: "12345678901",
        phone: "0555 111 22 33",
        job: "Mühendis",
        birth_date: "1990-01-01",
        hometown: "İzmir",
        reference: "Ahmet Bey",
        plate: "35 ABC 123",
        license: "R12345678",
        policy_type: "",
        insurance_company: "",
        due_date: "",
        agency: ""
    },
    {
        first_name: "Ayşe",
        last_name: "Demir",
        tc_id: "98765432100",
        phone: "0555 444 55 66",
        job: "Öğretmen",
        birth_date: "1985-05-15",
        hometown: "Ankara",
        reference: "Zeynep Hanım",
        plate: "06 DEF 456",
        license: "R87654321",
        policy_type: "",
        insurance_company: "",
        due_date: "",
        agency: ""
    }
];

const container = document.getElementById("cardContainer");

customers.forEach(customer => {
    const card = document.createElement("div");
    card.className = "card";

    card.innerHTML = `
    <strong>${customer.first_name} ${customer.last_name}</strong><br>
    <p><strong>TC:</strong> ${customer.tc_id}</p>
    <p><strong>Telefon:</strong> ${customer.phone}</p>
    <p><strong>Meslek:</strong> ${customer.job}</p>
    <p><strong>Doğum Tarihi:</strong> ${customer.birth_date}</p>
    <p><strong>Memleket:</strong> ${customer.hometown}</p>
    <p><strong>Referans:</strong> ${customer.reference}</p>

    <button class="toggle-btn">Detayları Gör</button>

    <div class="details">
      <p><strong>Plaka:</strong> ${customer.plate}</p>
      <p><strong>Ruhsat:</strong> ${customer.license}</p>

      <label><strong>Poliçe Türü:</strong></label>
      <select>
        <option>Kasko</option>
        <option>IMM</option>
        <option>Trafik</option>
        <option>FKS</option>
        <option>DASK</option>
        <option>Konut</option>
        <option>Seyahat Sağlık</option>
        <option>Tamamlayıcı Sağlık</option>
        <option>İşyeri</option>
        <option>Hekim Sorumluluk</option>
        <option>Eşya</option>
        <option>Tarsim</option>
        <option>Asistan</option>
        <option>Özel Sağlık</option>
        <option>Elementer</option>
      </select>

      <label><strong>Sigorta Şirketi:</strong></label>
      <input type="text" value="${customer.insurance_company}" />

      <label><strong>Vade Tarihi:</strong></label>
      <input type="date" value="${customer.due_date}" />

      <label><strong>Acente:</strong></label>
      <select>
        <option>Yakut</option>
        <option>Kirve</option>
        <option>BIC Sigorta</option>
        <option>Ege Ceren</option>
      </select>
    </div>
  `;

    container.appendChild(card);
});

document.addEventListener("click", function (e) {
    if (e.target.classList.contains("toggle-btn")) {
        const details = e.target.nextElementSibling;
        details.classList.toggle("visible");
    }
});
