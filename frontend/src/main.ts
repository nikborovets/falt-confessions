type ModerationStatus = 'pending' | 'blocked';
type ConfessionHistoryItem = {
  id: string;
  text: string;
  created_at: string; // ISO
  moderation_status: ModerationStatus;
  block_reason: string|null;
};

// Мок-API: подгрузка истории "с сервера"
function fetchUserHistory(): Promise<ConfessionHistoryItem[]> {
  // Фейковые данные (пример)
  const mock: ConfessionHistoryItem[] = [
    {
      id: 'a1',
      text: 'dnjskh',
      created_at: dateToIso(new Date(Date.now()-60*60*1000)),
      moderation_status: 'pending',
      block_reason: null
    },
    {
      id: 'a2',
      text: 'городок',
      created_at: dateToIso(new Date(Date.now()-2*60*60*1000)),
      moderation_status: 'blocked',
      block_reason: 'Неинтересный'
    },
    {
      id: 'a3',
      text: 'ещё один пост',
      created_at: dateToIso(new Date(Date.now()-4*60*60*1000)),
      moderation_status: 'pending',
      block_reason: null
    }
  ];
  return new Promise(resolve => setTimeout(() => resolve([...mock]), 600));
}

// Очистка истории (эмулируется)
function clearUserHistory(): Promise<void> {
  return new Promise(resolve => setTimeout(() => resolve(), 300));
}

function formatRuDatetime(iso: string): string {
  const d = new Date(iso);
  const day = d.getDate();
  const month =
    [
      'янв', 'фев', 'мар', 'апр', 'мая', 'июн',
      'июл', 'авг', 'сен', 'окт', 'ноя', 'дек',
    ][d.getMonth()];
  const hh = String(d.getHours()).padStart(2,'0');
  const mm = String(d.getMinutes()).padStart(2,'0');
  return `${day} ${month} в ${hh}:${mm}`;
}
function dateToIso(d: Date) {return d.toISOString();}

// Display loader
function showHistoryLoader() {
  const list = document.getElementById('history-list');
  if (list) list.innerHTML = '<div style="color:#FFF;margin:32px auto;text-align:center;font-size:20px;">Загрузка истории...</div>';
}

function renderServerHistory(confessions: ConfessionHistoryItem[]) {
  const historyHeader = document.querySelector('.history-header');
  if (historyHeader) {
      historyHeader.textContent = `История ваших последних ${confessions.length} постов`;
  }
  const historyList = document.getElementById('history-list');
  if (!historyList) return;
  historyList.innerHTML = '';
  if (!confessions.length) {
    historyList.innerHTML = '<div class="history-empty">История ваших постов пуста</div>';
    return;
  }
  confessions.forEach(post => {
    const card = document.createElement('div');
    card.className = 'history-card rich';
    card.innerHTML = `
      <div class="card-top-row">
        <span class="conf-logo">Confessions</span>
        <span class="card-date">${formatRuDatetime(post.created_at)}</span>
      </div>
      <div class="card-text">${escapeHtml(post.text)}</div>
      <div class="card-status-row">
        ${post.moderation_status==='pending' ?
          `<span class="status moderation">Ожидает модерации</span>` :
          `<span class="status blocked">Заблокировано: ${escapeHtml(post.block_reason||'')}</span>`
        }
        <span class="card-datelabel">${formatRuDatetime(post.created_at)}</span>
      </div>
    `;
    historyList.appendChild(card);
  });
}
function escapeHtml(html: string) {
  return html.replace(/[&<>"']/g, function(c) {return {'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;','\'':'&#39;'}[c]||c});
}

function triggerHistoryLoad() {
  showHistoryLoader();
  fetchUserHistory().then(renderServerHistory);
}
function triggerClearHistory() {
  showHistoryLoader();
  clearUserHistory().then(() => renderServerHistory([]));
}

// === Инициализация и навигация ===
document.addEventListener('DOMContentLoaded', () => {
  document.querySelectorAll('.icon-row label input[type="file"]').forEach((input) => {
    input.addEventListener('change', (e) => {
      if ((e.target as HTMLInputElement).files?.length) {
        alert('File(s) selected!');
      }
    });
  });
  const confessSection = document.getElementById('confess-section')!;
  const thankSection = document.getElementById('thank-section')!;
  const historySection = document.getElementById('history-section')!;
  const submitBtn = document.querySelector('.submit-btn') as HTMLButtonElement;
  const textArea = document.querySelector('.confession-input') as HTMLTextAreaElement;
  const backBtn = document.getElementById('back-btn') as HTMLAnchorElement;
  const historyBtn = document.getElementById('history-btn') as HTMLAnchorElement;
  const historyBackBtn = document.getElementById('history-back-btn') as HTMLAnchorElement;
  const historyClearBtn = document.getElementById('history-clear-btn') as HTMLButtonElement;
  const trackPostsIcons = document.querySelectorAll('.track-posts');

  function showSection(section: HTMLElement) {
    confessSection.style.display = 'none';
    thankSection.style.display = 'none';
    historySection.style.display = 'none';
    section.style.display = section.classList.contains('main-content') ? 'flex' : 'flex';
    window.scrollTo({ top: 0 });
  }

  // Навигация + demo сохранение только для UI
  if (submitBtn && textArea) {
    submitBtn.addEventListener('click', () => {
      if (!textArea.value.trim()) {
        alert('Пожалуйста, напишите Confession!');
        return;
      }
      showSection(thankSection);
      textArea.value = '';
    });
  }
  if (backBtn) {
    backBtn.addEventListener('click', (e) => {
      e.preventDefault();
      showSection(confessSection);
    });
  }
  if (historyBtn) {
    historyBtn.addEventListener('click', (e) => {
      e.preventDefault();
      showSection(historySection);
      triggerHistoryLoad();
    });
  }
  if (historyBackBtn) {
    historyBackBtn.addEventListener('click', (e) => {
      e.preventDefault();
      showSection(confessSection);
    });
  }
  if (historyClearBtn) {
    historyClearBtn.addEventListener('click', (e) => {
      e.preventDefault();
      triggerClearHistory();
    });
  }
  trackPostsIcons.forEach((icon) => {
    icon.addEventListener('click', (e) => {
      e.preventDefault();
      showSection(historySection);
      triggerHistoryLoad();
    });
  });
  showSection(confessSection);

  // Poll UI logic
  const pollSection = document.getElementById('poll-section')!;
  const pollToggleBtn = document.querySelector('.poll-toggle-icon') as HTMLImageElement;
  const pollRemoveBtn = document.querySelector('.poll-remove-btn') as HTMLButtonElement;
  const pollCloseAnswersBtn = document.querySelector('.poll-close-answers-btn') as HTMLButtonElement;
  const pollAnswersList = document.getElementById('poll-answers-list')!;
  const pollAddBtn = document.querySelector('.poll-add-btn') as HTMLButtonElement;
  const pollAnswerInput = document.querySelector('.poll-answer-input') as HTMLInputElement;
  const pollTopic = document.querySelector('.poll-topic') as HTMLInputElement;

  let pollActive = false;
  let answers: string[] = [];

  function renderPollAnswers() {
    pollAnswersList.innerHTML = '';
    answers.forEach((ans, i) => {
      const item = document.createElement('div');
      item.className = 'poll-answer-item';
      item.innerHTML = `${escapeHtml(ans)} <button class='poll-answer-delete' type='button' title='Удалить' data-idx='${i}'>✖</button>`;
      pollAnswersList.appendChild(item);
    });
    // delete handlers
    pollAnswersList.querySelectorAll('.poll-answer-delete').forEach(btn => {
      btn.addEventListener('click', (e) => {
        e.preventDefault();
        const idx = Number((e.currentTarget as HTMLElement).getAttribute('data-idx'));
        answers.splice(idx,1);
        renderPollAnswers();
        updatePollAddBtnState();
      });
    });
    updatePollAddBtnState();
  }

  function showPollForm(show: boolean) {
    pollSection.style.display = show ? 'block' : 'none';
    pollActive = show;
  }

  function updatePollAddBtnState() {
    // Запретить добавление, если меньше 2 вариантов или есть пустые/дубли
    if (pollAddBtn && pollAnswerInput) {
      const val = pollAnswerInput.value.trim();
      pollAddBtn.disabled = !val || answers.includes(val) || answers.length >= 10;
      pollAnswerInput.classList.toggle('input-error', !!val && answers.includes(val));
    }
    // Можно добавить еще логику для отображения ошибок/подсказок
  }

  if (pollToggleBtn) {
    pollToggleBtn.addEventListener('click', (e) => {
      e.preventDefault();
      pollActive = !pollActive;
      showPollForm(pollActive);
      if (pollActive) {
        pollTopic.value = '';
        pollAnswerInput.value = '';
        answers = [];
        renderPollAnswers();
      }
    });
  }
  if (pollRemoveBtn) {
    pollRemoveBtn.addEventListener('click', (e) => {
      e.preventDefault();
      showPollForm(false);
      pollTopic.value = '';
      pollAnswerInput.value = '';
      answers = [];
      renderPollAnswers();
    });
  }
  if (pollCloseAnswersBtn) {
    pollCloseAnswersBtn.addEventListener('click', (e) => {
      e.preventDefault();
      answers = [];
      renderPollAnswers();
    });
  }
  if (pollAddBtn && pollAnswerInput) {
    pollAddBtn.addEventListener('click', (e) => {
      e.preventDefault();
      const val = pollAnswerInput.value.trim();
      if (!val) return;
      if (answers.includes(val)) {
        pollAnswerInput.classList.add('input-error');
        return;
      }
      if (answers.length >= 10) return;
      answers.push(val);
      pollAnswerInput.value = '';
      renderPollAnswers();
    });
    pollAnswerInput.addEventListener('input', () => {
      updatePollAddBtnState();
    });
    pollAnswerInput.addEventListener('keypress', (e) => {
      if (e.key==='Enter') {
        e.preventDefault();
        pollAddBtn.click();
      }
    });
  }

  // Сбросить ошибки при фокусе
  if (pollAnswerInput) {
    pollAnswerInput.addEventListener('focus', () => {
      pollAnswerInput.classList.remove('input-error');
    });
  }

  // Можно добавить валидацию при отправке формы, чтобы не было меньше 2 вариантов
  if (submitBtn) {
    submitBtn.addEventListener('click', (e) => {
      if (pollActive) {
        if (!pollTopic.value.trim()) {
          alert('Пожалуйста, введите тему опроса!');
          pollTopic.focus();
          e.preventDefault();
          return;
        }
        if (answers.length < 2) {
          alert('Добавьте минимум два варианта ответа для опроса!');
          pollAnswerInput.focus();
          e.preventDefault();
          return;
        }
        // Можно добавить доп. валидацию на дубли и пустые строки, но UI уже не даст их добавить
      }
    });
  }
});
