(function () {
  'use strict';

  const API_BASE = ''; // тот же origin (backend раздаёт и API, и static)

  const yearSelect = document.getElementById('year');
  const monthSelect = document.getElementById('month');
  const studentSelect = document.getElementById('student_id');
  const form = document.getElementById('lesson-form');
  const btnSend = document.getElementById('btn-send');
  const btnPrint = document.getElementById('btn-print');
  const messageEl = document.getElementById('message');

  function showMessage(text, type) {
    messageEl.textContent = text;
    messageEl.className = 'message visible ' + (type || '');
  }

  function hideMessage() {
    messageEl.className = 'message';
  }

  function setYears() {
    const now = new Date();
    const current = now.getFullYear();
    for (let y = current - 1; y <= current + 1; y++) {
      const opt = document.createElement('option');
      opt.value = y;
      opt.textContent = y;
      if (y === current) opt.selected = true;
      yearSelect.appendChild(opt);
    }
  }

  function setMonths() {
    const months = [
      'Январь', 'Февраль', 'Март', 'Апрель', 'Май', 'Июнь',
      'Июль', 'Август', 'Сентябрь', 'Октябрь', 'Ноябрь', 'Декабрь'
    ];
    const now = new Date();
    const current = now.getMonth();
    months.forEach(function (name, i) {
      const opt = document.createElement('option');
      opt.value = i + 1;
      opt.textContent = name;
      if (i === current) opt.selected = true;
      monthSelect.appendChild(opt);
    });
  }

  function loadStudents() {
    studentSelect.innerHTML = '<option value="" disabled>— Загрузка... —</option>';
    studentSelect.disabled = true;
    fetch(API_BASE + '/api/students')
      .then(function (r) {
        if (!r.ok) throw new Error('Не удалось загрузить список студентов');
        return r.json();
      })
      .then(function (list) {
        studentSelect.innerHTML = '';
        var placeholder = document.createElement('option');
        placeholder.value = '';
        placeholder.disabled = true;
        placeholder.selected = true;
        placeholder.textContent = '— Выберите студента —';
        studentSelect.appendChild(placeholder);
        list.forEach(function (s) {
          var opt = document.createElement('option');
          opt.value = String(s.id);
          opt.textContent = s.full_name || (s.first_name + ' ' + s.last_name);
          studentSelect.appendChild(opt);
        });
        studentSelect.disabled = false;
      })
      .catch(function (err) {
        studentSelect.innerHTML = '<option value="" disabled>— Ошибка загрузки —</option>';
        studentSelect.disabled = false;
        showMessage(err.message || 'Ошибка загрузки студентов', 'error');
      });
  }

  function getFormPayload() {
    return {
      student_id: parseInt(studentSelect.value, 10),
      year: parseInt(yearSelect.value, 10),
      month: parseInt(monthSelect.value, 10),
      grammar_e: form.grammar_e.value.trim(),
      reading_e: form.reading_e.value.trim(),
      speaking_e: form.speaking_e.value.trim(),
      writing_e: form.writing_e.value.trim(),
      hours_studied: parseInt(form.hours_studied.value, 10) || 1
    };
  }

  function validatePayload(payload) {
    if (!payload.student_id) {
      showMessage('Выберите студента', 'error');
      return false;
    }
    if (payload.hours_studied < 1 || payload.hours_studied > 12) {
      showMessage('Количество часов: от 1 до 12', 'error');
      return false;
    }
    return true;
  }

  form.addEventListener('submit', function (e) {
    e.preventDefault();
    hideMessage();
    var payload = getFormPayload();
    if (!validatePayload(payload)) return;

    btnSend.disabled = true;
    fetch(API_BASE + '/api/lessons', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    })
      .then(function (r) {
        if (!r.ok) return r.json().then(function (d) { throw new Error(d.detail || 'Ошибка сохранения'); });
        return r.json();
      })
      .then(function () {
        showMessage('Данные сохранены', 'success');
      })
      .catch(function (err) {
        showMessage(err.message || 'Ошибка отправки данных', 'error');
      })
      .finally(function () {
        btnSend.disabled = false;
      });
  });

  btnPrint.addEventListener('click', function () {
    hideMessage();
    var payload = getFormPayload();
    if (!payload.student_id) {
      showMessage('Выберите студента для отчёта', 'error');
      return;
    }

    var url = API_BASE + '/api/report/pdf?student_id=' + payload.student_id +
      '&year=' + payload.year + '&month=' + payload.month;
    window.open(url, '_blank');
    showMessage('Отчёт открыт в новой вкладке. Если не открылся — проверьте, что данные за этот период сохранены.', 'success');
  });

  function loadExistingLesson() {
    var payload = getFormPayload();
    if (!payload.student_id) return;
    var q = '?student_id=' + payload.student_id + '&year=' + payload.year + '&month=' + payload.month;
    fetch(API_BASE + '/api/lessons' + q)
      .then(function (r) {
        if (!r.ok || r.status === 204) return;
        return r.json();
      })
      .then(function (data) {
        if (!data) return;
        form.grammar_e.value = data.grammar_e || '';
        form.reading_e.value = data.reading_e || '';
        form.speaking_e.value = data.speaking_e || '';
        form.writing_e.value = data.writing_e || '';
        form.hours_studied.value = data.hours_studied || 1;
      })
      .catch(function () {});
  }

  yearSelect.addEventListener('change', loadExistingLesson);
  monthSelect.addEventListener('change', loadExistingLesson);
  studentSelect.addEventListener('change', loadExistingLesson);

  setYears();
  setMonths();
  loadStudents();
})();
