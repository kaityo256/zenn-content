# frozen_string_literal: true

require "net/http"
require "uri"
require "json"

# 保存する URL と出力ファイル名
API_URL = "https://zenn.dev/api/articles?username=kaityo256"
OUTPUT_FILE = "zenn.json"

def fetch_json(url)
  uri = URI.parse(url)
  response = Net::HTTP.get_response(uri)

  unless response.is_a?(Net::HTTPSuccess)
    raise "Request failed: #{response.code} #{response.message}"
  end

  response.body
end

def save_to_file(json_str, path)
  File.open(path, "w") do |file|
    file.write(json_str)
  end
  puts "Saved JSON to #{path}"
end

# 実行
begin
  json_data = fetch_json(API_URL)
  save_to_file(json_data, OUTPUT_FILE)
rescue StandardError => e
  warn "[ERROR] #{e.class}: #{e.message}"
  exit 1
end
