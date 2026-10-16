/* Teleporta — utilitários compartilhados: idioma (PT/EN), ícones, avisos. */
(() => {
  const D = {
    pt: {
      'connect.title': 'Conecte o celular',
      'connect.help': 'PC e celular no mesmo Wi-Fi. Aponte a câmera do celular para o código.',
      'connect.or': 'Ou abra o endereço no navegador do celular e digite o PIN:',
      'status.wait': 'Esperando o celular…',
      'status.on': 'Conectado: {names}',
      'chip.free': 'Grátis · {used}/{limit} hoje',
      'tab.files': 'Arquivos', 'tab.text': 'Texto e links', 'tab.history': 'Histórico', 'tab.plan': 'Plano',
      'recv.title': 'Recebidos do celular', 'recv.saving': 'Salvando em', 'recv.receiving': 'Recebendo…',
      'recv.empty': 'Nada por aqui ainda. Envie algo do celular e aparece em segundos.',
      'open.folder': 'Abrir pasta', 'zip.all': 'Tudo em ZIP', 'zip.outbox': 'Baixar tudo em ZIP',
      'send.title': 'Enviar para o celular',
      'send.drop': 'Solte arquivos aqui, cole com Ctrl+V ou clique para escolher',
      'send.copying': 'Copiando {n} de {total}: {name}',
      'send.done': '{n} no celular. Abra a aba Receber.',
      'send.empty': 'Nada esperando o celular.',
      'toast.received': 'Recebido: {name}',
      'delete': 'Apagar', 'delete.confirm': 'Apagar?', 'remove': 'Remover',
      'limit.hit': 'Você usou os {limit} arquivos grátis de hoje. Com o Pro, sem limite.',
      'cta.pro': 'Ver o Pro', 'pro.only': 'Recurso do Pro.', 'badge.pro': 'Pro',
      'text.title': 'Texto e links',
      'text.ph': 'Escreva ou cole um texto ou link para o celular…',
      'text.send': 'Enviar', 'text.copy': 'Copiar', 'text.copied': 'Copiado',
      'text.empty': 'Nada por aqui. Mande um link do PC para o celular, ou o contrário.',
      'hist.title': 'Histórico', 'hist.files': 'arquivos', 'hist.in': 'recebidos do celular', 'hist.out': 'enviados ao celular',
      'hist.days': 'Arquivos por dia, últimos 14 dias', 'hist.empty': 'Ainda sem transferências.',
      'hist.from': 'de {dev}', 'hist.to': 'para o celular',
      'hist.locked.title': 'Histórico e estatísticas',
      'hist.locked.desc': 'Veja tudo que já passou pelo Teleporta: quando, de qual aparelho e quanto. Faz parte do Pro.',
      'plan.free.title': 'Plano grátis', 'plan.free.badge': 'Grátis',
      'plan.free.desc': '{used} de {limit} arquivos usados hoje. O contador zera à meia-noite.',
      'plan.pro.title': 'Pro ativo',
      'plan.pro.desc': 'Licença de {email}. Obrigado por apoiar o Teleporta.',
      'feat.free1': 'Fotos, vídeos e arquivos nos dois sentidos, sem recompressão',
      'feat.free2': 'Textos e links entre celular e PC',
      'feat.pro1': 'Sem limite diário de arquivos',
      'feat.pro2': 'Organiza os recebidos por data da foto ou por tipo',
      'feat.pro3': 'Pareamento fixo: escaneia uma vez e o celular continua conectado',
      'feat.pro4': 'Baixa vários arquivos de uma vez em ZIP',
      'feat.pro5': 'Histórico e estatísticas de transferência',
      'plan.have': 'Já tem uma chave?',
      'plan.key.ph': 'Cole a chave de licença aqui',
      'plan.activate': 'Ativar',
      'plan.buy': 'Comprar o Pro',
      'plan.ok': 'Pro ativado. Obrigado!',
      'plan.bad': 'Chave inválida. Confira se copiou inteira, sem espaços faltando.',
      'settings.title': 'Ajustes do Pro', 'settings.saved': 'Salvo',
      'organize.title': 'Organizar recebidos',
      'organize.off': 'Tudo na mesma pasta', 'organize.date': 'Por data da foto', 'organize.type': 'Por tipo (Fotos, Videos…)',
      'fixed.title': 'Pareamento fixo',
      'fixed.desc': 'Mantém o PIN e o QR code iguais e o celular conectado por 30 dias.',
      'p.tab.send': 'Enviar', 'p.tab.recv': 'Receber', 'p.tab.text': 'Texto',
      'p.connected': 'Conectado a {host}', 'p.offline': 'Sem conexão com o PC',
      'p.free.left': '{n} grátis hoje',
      'p.limit.hit': 'Acabaram os {limit} arquivos grátis de hoje. Ative o Pro no PC para continuar.',
      'p.pick': 'Escolher fotos, vídeos ou arquivos',
      'p.pick.sub': 'Qualquer tipo: zip, PDF, planilhas…',
      'p.keep': 'Mantenha esta tela aberta até terminar.',
      'p.queued': 'Na fila', 'p.sending': 'Enviando…',
      'p.sum.sending': 'Enviando {n} de {total} · {sent} de {all}',
      'p.sum.done': 'Tudo enviado ({n} arquivos, {size})',
      'p.sum.partial': '{ok} enviados, {bad} não enviados',
      'p.err.limit': 'Limite grátis de hoje atingido', 'p.err.send': 'Erro ao enviar', 'p.err.lost': 'Conexão perdida',
      'p.ios.title': 'Dica: enviar na qualidade original',
      'p.ios.body': 'No iPhone, abra Ajustes → Fotos → role até o fim → <b>Transferir para Mac ou PC</b> → marque <b>Manter originais</b>. Assim o Safari não converte HEIC em JPEG nem recomprime vídeos.',
      'p.recv.help': 'Arquivos que o PC deixou para você. Toque em Baixar para salvar no celular.',
      'p.recv.help.ios': 'Arquivos que o PC deixou para você. Em fotos e vídeos, toque em Abrir e use o botão de compartilhar para salvar em Fotos.',
      'p.recv.empty': 'Nada por aqui. No PC, arraste arquivos para “Enviar para o celular”.',
      'p.open': 'Abrir', 'p.download': 'Baixar',
      'p.pro.only': 'Baixar em ZIP é do Pro. Ative no PC.',
      'p.text.ph': 'Escreva ou cole um texto ou link para o PC…',
      'login.title': 'Conectar ao PC',
      'login.help': 'Digite o PIN de 6 dígitos que aparece na tela do computador.',
      'login.btn': 'Conectar',
      'login.bad': 'PIN incorreto. Confira o número na tela do PC.',
      'login.locked': 'Muitas tentativas. Espere {s} segundos.',
      'login.offline': 'Sem conexão com o PC. Confira se os dois estão no mesmo Wi-Fi.',
    },
    en: {
      'connect.title': 'Connect your phone',
      'connect.help': 'PC and phone on the same Wi-Fi. Point your phone camera at the code.',
      'connect.or': 'Or open this address in your phone browser and enter the PIN:',
      'status.wait': 'Waiting for your phone…',
      'status.on': 'Connected: {names}',
      'chip.free': 'Free · {used}/{limit} today',
      'tab.files': 'Files', 'tab.text': 'Text & links', 'tab.history': 'History', 'tab.plan': 'Plan',
      'recv.title': 'Received from phone', 'recv.saving': 'Saving to', 'recv.receiving': 'Receiving…',
      'recv.empty': 'Nothing here yet. Send something from your phone and it shows up in seconds.',
      'open.folder': 'Open folder', 'zip.all': 'All as ZIP', 'zip.outbox': 'Download all as ZIP',
      'send.title': 'Send to phone',
      'send.drop': 'Drop files here, paste with Ctrl+V, or click to choose',
      'send.copying': 'Copying {n} of {total}: {name}',
      'send.done': '{n} ready on your phone. Open the Receive tab.',
      'send.empty': 'Nothing waiting for the phone.',
      'toast.received': 'Received: {name}',
      'delete': 'Delete', 'delete.confirm': 'Delete?', 'remove': 'Remove',
      'limit.hit': 'You used today’s {limit} free files. Pro has no limit.',
      'cta.pro': 'See Pro', 'pro.only': 'Pro feature.', 'badge.pro': 'Pro',
      'text.title': 'Text & links',
      'text.ph': 'Write or paste text or a link for your phone…',
      'text.send': 'Send', 'text.copy': 'Copy', 'text.copied': 'Copied',
      'text.empty': 'Nothing here. Send a link from PC to phone, or the other way around.',
      'hist.title': 'History', 'hist.files': 'files', 'hist.in': 'received from phone', 'hist.out': 'sent to phone',
      'hist.days': 'Files per day, last 14 days', 'hist.empty': 'No transfers yet.',
      'hist.from': 'from {dev}', 'hist.to': 'to phone',
      'hist.locked.title': 'History and stats',
      'hist.locked.desc': 'See everything that went through Teleporta: when, from which device, and how much. Part of Pro.',
      'plan.free.title': 'Free plan', 'plan.free.badge': 'Free',
      'plan.free.desc': '{used} of {limit} files used today. The counter resets at midnight.',
      'plan.pro.title': 'Pro is active',
      'plan.pro.desc': 'Licensed to {email}. Thanks for supporting Teleporta.',
      'feat.free1': 'Photos, videos and files both ways, never recompressed',
      'feat.free2': 'Text and links between phone and PC',
      'feat.pro1': 'No daily file limit',
      'feat.pro2': 'Sorts received files by photo date or by type',
      'feat.pro3': 'Fixed pairing: scan once and your phone stays connected',
      'feat.pro4': 'Download many files at once as a ZIP',
      'feat.pro5': 'Transfer history and stats',
      'plan.have': 'Already have a key?',
      'plan.key.ph': 'Paste your license key here',
      'plan.activate': 'Activate',
      'plan.buy': 'Buy Pro',
      'plan.ok': 'Pro activated. Thank you!',
      'plan.bad': 'Invalid key. Check that you copied all of it.',
      'settings.title': 'Pro settings', 'settings.saved': 'Saved',
      'organize.title': 'Sort received files',
      'organize.off': 'Everything in one folder', 'organize.date': 'By photo date', 'organize.type': 'By type (Fotos, Videos…)',
      'fixed.title': 'Fixed pairing',
      'fixed.desc': 'Keeps the PIN and QR code the same and your phone connected for 30 days.',
      'p.tab.send': 'Send', 'p.tab.recv': 'Receive', 'p.tab.text': 'Text',
      'p.connected': 'Connected to {host}', 'p.offline': 'No connection to the PC',
      'p.free.left': '{n} free today',
      'p.limit.hit': 'Today’s {limit} free files are used up. Activate Pro on the PC to keep going.',
      'p.pick': 'Choose photos, videos or files',
      'p.pick.sub': 'Any type: zip, PDF, spreadsheets…',
      'p.keep': 'Keep this screen open until it finishes.',
      'p.queued': 'Queued', 'p.sending': 'Sending…',
      'p.sum.sending': 'Sending {n} of {total} · {sent} of {all}',
      'p.sum.done': 'All sent ({n} files, {size})',
      'p.sum.partial': '{ok} sent, {bad} not sent',
      'p.err.limit': 'Free limit reached today', 'p.err.send': 'Upload failed', 'p.err.lost': 'Connection lost',
      'p.ios.title': 'Tip: send in original quality',
      'p.ios.body': 'On iPhone, open Settings → Photos → scroll to the end → <b>Transfer to Mac or PC</b> → choose <b>Keep Originals</b>. This stops Safari from converting HEIC to JPEG or recompressing videos.',
      'p.recv.help': 'Files the PC left for you. Tap Download to save to your phone.',
      'p.recv.help.ios': 'Files the PC left for you. For photos and videos, tap Open and use the share button to save to Photos.',
      'p.recv.empty': 'Nothing here. On the PC, drag files into “Send to phone”.',
      'p.open': 'Open', 'p.download': 'Download',
      'p.pro.only': 'ZIP download is a Pro feature. Activate it on the PC.',
      'p.text.ph': 'Write or paste text or a link for the PC…',
      'login.title': 'Connect to PC',
      'login.help': 'Enter the 6-digit PIN shown on your computer screen.',
      'login.btn': 'Connect',
      'login.bad': 'Wrong PIN. Check the number on the PC screen.',
      'login.locked': 'Too many tries. Wait {s} seconds.',
      'login.offline': 'No connection to the PC. Check that both are on the same Wi-Fi.',
    },
  };

  let L = null;
  try { L = localStorage.getItem('tp_lang'); } catch {}
  if (!D[L]) L = /^en/i.test(navigator.language || '') ? 'en' : 'pt';
  document.documentElement.lang = L === 'pt' ? 'pt-BR' : 'en';

  const t = (k, v) => {
    let s = D[L][k] ?? D.pt[k] ?? k;
    if (v) for (const x in v) s = s.replaceAll('{' + x + '}', v[x]);
    return s;
  };
  const $ = (s, r = document) => r.querySelector(s);
  const $$ = (s, r = document) => [...r.querySelectorAll(s)];
  const esc = s => String(s).replace(/[&<>"']/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]));
  const fmt = n => n < 1024 ? n + ' B' : n < 1048576 ? (n / 1024).toFixed(0) + ' KB' : n < 1073741824 ? (n / 1048576).toFixed(1) + ' MB' : (n / 1073741824).toFixed(2) + ' GB';
  const ago = ts => {
    const s = Math.max(0, Date.now() / 1000 - ts);
    const pt = L === 'pt';
    return s < 60 ? (pt ? 'agora' : 'just now')
      : s < 3600 ? Math.floor(s / 60) + (pt ? ' min atrás' : ' min ago')
      : s < 86400 ? Math.floor(s / 3600) + (pt ? ' h atrás' : ' h ago')
      : new Date(ts * 1000).toLocaleDateString(pt ? 'pt-BR' : 'en-US');
  };

  const ICONS = {
    file: '<path d="M14 3H7a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h10a2 2 0 0 0 2-2V8z"/><path d="M14 3v5h5"/>',
    doc: '<path d="M14 3H7a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h10a2 2 0 0 0 2-2V8z"/><path d="M14 3v5h5M9 13h6M9 17h6"/>',
    zip: '<path d="M14 3H7a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h10a2 2 0 0 0 2-2V8z"/><path d="M14 3v5h5M10 11h2M10 14h2M10 17h2"/>',
    image: '<rect x="3" y="4" width="18" height="16" rx="2"/><circle cx="9" cy="10" r="1.6"/><path d="m21 16-5-5-8 9"/>',
    video: '<rect x="3" y="5" width="13" height="14" rx="2"/><path d="m16 10 5-3v10l-5-3"/>',
    audio: '<path d="M9 18V6l10-2v12"/><circle cx="6.5" cy="18" r="2.5"/><circle cx="16.5" cy="16" r="2.5"/>',
    up: '<path d="M12 19V5M5 12l7-7 7 7"/>',
    down: '<path d="M12 5v14M5 12l7 7 7-7"/>',
    copy: '<rect x="9" y="9" width="11" height="11" rx="2"/><path d="M5 15V6a2 2 0 0 1 2-2h8"/>',
    trash: '<path d="M4 7h16M10 11v6M14 11v6M6 7l1 13h10l1-13M9 7V4h6v3"/>',
    x: '<path d="M6 6l12 12M18 6 6 18"/>',
    check: '<path d="m5 12.5 4.5 4.5L19 7"/>',
    lock: '<rect x="5" y="11" width="14" height="10" rx="2"/><path d="M8 11V8a4 4 0 0 1 8 0v3"/>',
    bolt: '<path d="M13 2 4 14h7l-1 8 9-12h-7z"/>',
  };
  const ico = name => `<svg class="i" viewBox="0 0 24 24" aria-hidden="true">${ICONS[name] || ICONS.file}</svg>`;
  const KINDS = [
    [/\.(jpe?g|png|gif|webp|bmp|heic|heif)$/i, 'image'], [/\.(zip|rar|7z|tar|gz)$/i, 'zip'],
    [/\.(pdf|docx?|odt|rtf|txt|xlsx?|csv|pptx?|key)$/i, 'doc'], [/\.(mp3|m4a|wav|aac|flac|ogg|opus)$/i, 'audio'],
  ];
  const kindIcon = name => (KINDS.find(([re]) => re.test(name)) || [0, 'file'])[1];

  const toast = (msg, kind) => {
    let box = $('#toasts');
    if (!box) { box = document.createElement('div'); box.id = 'toasts'; box.setAttribute('role', 'status'); document.body.append(box); }
    const el = document.createElement('div');
    el.className = 'toast' + (kind === 'err' ? ' err' : '');
    el.textContent = msg;
    box.append(el);
    setTimeout(() => el.remove(), 3800);
  };

  // Escapa o texto e só então transforma http(s):// em link clicável.
  const linkify = text => esc(text).replace(/https?:\/\/[^\s<]+/g, u => `<a href="${u}" target="_blank" rel="noopener noreferrer">${u}</a>`);

  const copyText = async text => {
    try { await navigator.clipboard.writeText(text); return; } catch {}
    const ta = document.createElement('textarea');  // páginas em http:// no celular não têm navigator.clipboard
    ta.value = text; ta.style.cssText = 'position:fixed;opacity:0';
    document.body.append(ta); ta.select(); ta.setSelectionRange(0, text.length);
    try { document.execCommand('copy'); } catch {}
    ta.remove();
  };

  const applyI18n = () => {
    $$('[data-i18n]').forEach(el => { el.textContent = t(el.dataset.i18n); });
    $$('[data-i18n-ph]').forEach(el => { el.placeholder = t(el.dataset.i18nPh); });
    $$('[data-i18n-html]').forEach(el => { el.innerHTML = t(el.dataset.i18nHtml); });
  };
  const langButton = el => {
    el.textContent = L === 'pt' ? 'EN' : 'PT';
    el.title = L === 'pt' ? 'English' : 'Português';
    el.onclick = () => { try { localStorage.setItem('tp_lang', L === 'pt' ? 'en' : 'pt'); } catch {} location.reload(); };
  };

  window.TP = { t, $, $$, esc, fmt, ago, ico, kindIcon, toast, linkify, copyText, applyI18n, langButton, D };
})();
