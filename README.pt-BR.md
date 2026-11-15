# TTLock BLE RW para Home Assistant

Fork público de `roquerodrigo/ha-ttlock-ble`, baseado na versão upstream 3.13.0. Mantém domínio `ttlock_ble`, entidades e configuração existentes. A documentação técnica completa está em [English](README.md).

## Serviços de senha

Este fork acrescenta comandos locais por Bluetooth para fechaduras administradas:

- `ttlock_ble.add_passcode`: cria senha de teclado com 4 a 9 dígitos. Use `PERMANENT` (padrão), ou `PERIOD` com `start_date` e `end_date` no formato `YYMMDDHHmm`.
- `ttlock_ble.delete_passcode`: remove a senha exata de 4 a 9 dígitos. A remoção é irreversível na fechadura.

Os serviços não gravam, mostram ou registram a senha no estado, histórico, diagnósticos ou logs do Home Assistant. Alguns firmwares TTLock aceitam prefixos menores: nunca crie senhas com prefixos em comum.

## Instalação pelo HACS

1. Em HACS, abra **Integrações** e adicione este repositório como repositório personalizado.
2. Instale a versão mais recente e reinicie o Home Assistant.
3. Mantenha a configuração atual da integração **TTLock BLE**. Não é necessário remover nem recriar fechaduras.

## Atualização e rollback

Atualize pelo HACS após validar cada release. Para rollback, escolha a release anterior na página do repositório no HACS e reinicie o Home Assistant. Este fork incorpora mudanças upstream somente após revisão manual, testes e validação de compatibilidade.

## Limitações

- Criação e remoção exigem chave administrativa, alcance Bluetooth e uma fechadura que aceite esses comandos.
- A listagem de senhas depende do recurso de leitura já disponibilizado no ambiente; nem todo firmware revela senhas ainda não usadas.
- Nunca teste comandos em fechaduras de produção sem identificar a entidade correta.
