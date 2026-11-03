import os
import re
import sys
import glob

REF_FILE = os.path.join(os.path.dirname(__file__), '../02 — Professor · Mobile/painel-inicial.html')

def normalize_svg(svg_str):
    return re.sub(r'\s+', ' ', svg_str).strip()

def run_checks(file_path, ref_content):
    errors = []
    content = open(file_path, 'r', encoding='utf-8').read()
    filename = os.path.basename(file_path)

    if '<script' in content.lower():
        errors.append(f'[{filename}] VIOLAÇÃO DE CÓDIGO: Encontrada tag <script> (deve ser 100% puro HTML/CSS).')
    if '<!--' in content:
        errors.append(f'[{filename}] VIOLAÇÃO DE CÓDIGO: Encontrado comentário HTML <!-- --> (deve ser 0 comentários).')
    if '/*' in content:
        errors.append(f'[{filename}] VIOLAÇÃO DE CÓDIGO: Encontrado comentário CSS /* */ (deve ser 0 comentários).')

    ref_header_match = re.search(r'<header[^>]*class=\"[^\"]*mobile-header[^\"]*\"[^>]*>(.*?)</header>', ref_content, re.DOTALL)
    tgt_header_match = re.search(r'<header[^>]*class=\"[^\"]*mobile-header[^\"]*\"[^>]*>(.*?)</header>', content, re.DOTALL)

    if not tgt_header_match:
        errors.append(f'[{filename}] ETAPA 3: Elemento <header class="mobile-header"> não encontrado.')
    else:
        ref_header_svgs = re.findall(r'<svg[^>]*>.*?</svg>', ref_header_match.group(1), re.DOTALL)
        tgt_header_svgs = re.findall(r'<svg[^>]*>.*?</svg>', tgt_header_match.group(1), re.DOTALL)

        if len(tgt_header_svgs) < 3:
            errors.append(f'[{filename}] ETAPA 1 (Header): Esperados 3 SVGs no cabeçalho (Logo, Mensagens, Notificações), encontrados {len(tgt_header_svgs)}.')
        else:
            if 'M3.333 16.25c0-1.15.933-2.083 2.084-2.083h11.25' not in tgt_header_svgs[0]:
                errors.append(f'[{filename}] ETAPA 1 (Header Logo): SVG do caderno divergente do padrão.')
            if 'M2.5 4.583C2.5 3.433' not in tgt_header_svgs[1] or 'M14.167 5.833h1.25' not in tgt_header_svgs[1]:
                errors.append(f'[{filename}] ETAPA 1 (Header Mensagens): SVG multibalão de 3 caminhos divergente do padrão.')
            if 'M10.333 23.5h3.334' not in tgt_header_svgs[2]:
                errors.append(f'[{filename}] ETAPA 1 (Header Notificações): SVG do sino (viewBox 0 0 24 24, base M10.333 23.5) divergente.')
            if 'notif-badge-dot' not in tgt_header_match.group(1):
                errors.append(f'[{filename}] ETAPA 1 (Header Notificações): Indicador .notif-badge-dot ausente.')

    ref_nav_match = re.search(r'<nav[^>]*class=\"[^\"]*bottom-nav[^\"]*\"[^>]*>(.*?)</nav>', ref_content, re.DOTALL)
    tgt_nav_match = re.search(r'<nav[^>]*class=\"[^\"]*bottom-nav[^\"]*\"[^>]*>(.*?)</nav>', content, re.DOTALL)

    if not tgt_nav_match:
        errors.append(f'[{filename}] ETAPA 3: Elemento <nav class="bottom-nav"> não encontrado.')
    else:
        tgt_nav_svgs = re.findall(r'<svg[^>]*>.*?</svg>', tgt_nav_match.group(1), re.DOTALL)
        if len(tgt_nav_svgs) < 4:
            errors.append(f'[{filename}] ETAPA 1 (Footer): Esperados 4 SVGs (Início, Turmas, Registros, Perfil), encontrados {len(tgt_nav_svgs)}.')
        else:
            if 'M2.5 8.333L10 2.5l7.5 5.833' not in tgt_nav_svgs[0]:
                errors.append(f'[{filename}] ETAPA 1 (Footer Início): SVG de Início divergente.')
            if 'M10 5.833v11.667' not in tgt_nav_svgs[1]:
                errors.append(f'[{filename}] ETAPA 1 (Footer Turmas): SVG de Turmas divergente.')
            if 'M11.667 1.667H5' not in tgt_nav_svgs[2]:
                errors.append(f'[{filename}] ETAPA 1 (Footer Registros): SVG de Registros divergente.')
            if '<circle cx="10" cy="6.667" r="3.333"/>' not in tgt_nav_svgs[3]:
                errors.append(f'[{filename}] ETAPA 1 (Footer Perfil): SVG de Perfil divergente (esperado formato Penpot u41e65023-41aa-8015-8008-d3768e6b55f7).')

    if 'fonts.googleapis.com/css2?family=Inter' not in content:
        errors.append(f'[{filename}] ETAPA 2 (Tipografia): Fonte Inter não importada.')
    if '-webkit-font-smoothing: antialiased' not in content:
        errors.append(f'[{filename}] ETAPA 2 (Tipografia): -webkit-font-smoothing: antialiased ausente.')
    if 'Educar &amp; Aprender' not in content and 'Educar & Aprender' not in content:
        errors.append(f'[{filename}] ETAPA 2 (Hierarquia): Marca Educar & Aprender não encontrada.')
    if 'Área do Professor' not in content and 'ÁREA DO PROFESSOR' not in content:
        errors.append(f'[{filename}] ETAPA 2 (Hierarquia): Subtítulo Área do Professor não encontrado.')

    if 'modal-perfil' not in content:
        errors.append(f'[{filename}] ETAPA 3 (Modal): Estrutura #modal-perfil não encontrada.')
    if 'profile-modal-pointer' not in content:
        errors.append(f'[{filename}] ETAPA 3 (Modal): .profile-modal-pointer não encontrado.')

    return errors

def main():
    if not os.path.exists(REF_FILE):
        print(f'Erro: Arquivo de referência {REF_FILE} não encontrado.')
        sys.exit(1)

    ref_content = open(REF_FILE, 'r', encoding='utf-8').read()

    target_files = sys.argv[1:] if len(sys.argv) > 1 else sorted(glob.glob(os.path.join(os.path.dirname(REF_FILE), '*.html')))

    all_passed = True
    total_checked = 0

    print('=' * 70)
    print('SUÍTE DE TESTES: PADRONIZAÇÃO PROFESSOR MOBILE')
    print('Verificando: SVGs Exatos, Tipografia Inter, Geometria CSS e Clean Code')
    print('=' * 70)

    for f in target_files:
        if not os.path.isfile(f):
            continue
        total_checked += 1
        errs = run_checks(f, ref_content)
        name = os.path.basename(f)
        if errs:
            all_passed = False
            print(f'❌ {name}: FALHOU ({len(errs)} erros):')
            for e in errs:
                print(f'   - {e}')
        else:
            print(f'✅ {name}: 100% CONFORME')

    print('=' * 70)
    if all_passed:
        print(f'RESULTADO: SUCESSO TOTAL! Todos os {total_checked} arquivos estão 100% padronizados.')
        sys.exit(0)
    else:
        print(f'RESULTADO: FALHA em um ou mais arquivos checados.')
        sys.exit(1)

if __name__ == '__main__':
    main()
